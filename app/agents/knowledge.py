import os
import json
import logging
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
from app.models import InternalDoc
from app.database import is_sqlite

logger = logging.getLogger(__name__)

# text-embedding-004 was deprecated/shut down by Google. gemini-embedding-001
# (text-only) is tried first since this app only ever embeds text; gemini-embedding-2
# (multimodal, newer) is the fallback if the primary model is unavailable for the
# account/API key. Both default to 3072-dim output, pinned to 768 via
# output_dimensionality below to fit the existing Vector(768) schema.
FALLBACK_EMBEDDING_MODELS = ["gemini-embedding-001", "gemini-embedding-2"]

class KnowledgeAgent:
    """
    KnowledgeAgent is responsible for generating vector embeddings for text chunks,
    and performing semantic similarity searches across the company's internal documents.
    """

    @classmethod
    def get_client(cls) -> genai.Client | None:
        """Initializes the Google GenAI client if API key is provided."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            logger.warning(f"Failed to initialize genai.Client: {e}")
            return None

    @classmethod
    def get_embedding(cls, text_content: str) -> list[float]:
        """
        Generates a 768-dimension vector embedding, trying each candidate model in
        turn (GEMINI_EMBEDDING_MODEL env var first if set, then the built-in
        fallback chain) so a single unavailable model doesn't break embeddings.
        """
        client = cls.get_client()
        if not client:
            return [0.0] * 768

        configured_model = os.getenv("GEMINI_EMBEDDING_MODEL")
        candidates = list(FALLBACK_EMBEDDING_MODELS)
        if configured_model and configured_model not in candidates:
            candidates.insert(0, configured_model)
        elif configured_model:
            candidates.remove(configured_model)
            candidates.insert(0, configured_model)

        last_error = None
        for model_name in candidates:
            try:
                response = client.models.embed_content(
                    model=model_name,
                    contents=text_content,
                    config=types.EmbedContentConfig(output_dimensionality=768)
                )
                return response.embeddings[0].values
            except Exception as e:
                last_error = e
                logger.warning(f"Embedding model '{model_name}' failed, trying next fallback: {e}")

        logger.error(f"Error generating embedding after trying all fallback models: {last_error}")
        # Mock vector of 768 zeros if all candidates fail (graceful degradation)
        return [0.0] * 768


    @classmethod
    def search_similar_docs(cls, query_text: str, db: Session, limit: int = 5) -> list[tuple[InternalDoc, float]]:
        """
        Searches the internal_docs table for documents semantically similar to query_text.
        Supports SQLite (via python cosine_similarity function) and PostgreSQL (via pgvector <=>).
        """
        query_vector = cls.get_embedding(query_text)
        
        try:
            if is_sqlite:
                # Query all documents, calculating similarity using custom sqlite function
                query_vector_str = json.dumps(query_vector)
                
                # Execute query calculating similarity
                raw_query = text(
                    "SELECT id, cosine_similarity(embedding, :query_vec) AS similarity "
                    "FROM internal_docs ORDER BY similarity DESC LIMIT :limit"
                )
                res = db.execute(raw_query, {"query_vec": query_vector_str, "limit": limit}).fetchall()
                
                # Map results to models
                matched_docs = []
                for row in res:
                    doc_id = row[0]
                    similarity = row[1]
                    doc = db.query(InternalDoc).filter(InternalDoc.id == doc_id).first()
                    if doc:
                        matched_docs.append((doc, float(similarity)))
                return matched_docs
            else:
                # PostgreSQL pgvector approach
                # pgvector <=> operator is cosine distance (1 - cosine similarity)
                # We sort by cosine distance ascending (closest first)
                # Note: pgvector can be queried using raw SQL text or pgvector model mapping
                # NOTE: :query_vec::vector (no space) is NOT recognized by
                # SQLAlchemy's text() as a bind parameter - the trailing `::`
                # cast makes it treat the whole token as literal SQL, so
                # ":query_vec" is sent to Postgres unsubstituted and fails
                # with a syntax error. CAST(:query_vec AS vector) compiles
                # correctly (verified via query.compile()).
                raw_query = text(
                    "SELECT id, (1 - (embedding <=> CAST(:query_vec AS vector))) AS similarity "
                    "FROM internal_docs ORDER BY embedding <=> CAST(:query_vec AS vector) ASC LIMIT :limit"
                )
                res = db.execute(raw_query, {"query_vec": str(query_vector), "limit": limit}).fetchall()
                
                matched_docs = []
                for row in res:
                    doc_id = row[0]
                    similarity = row[1]
                    doc = db.query(InternalDoc).filter(InternalDoc.id == doc_id).first()
                    if doc:
                        matched_docs.append((doc, float(similarity)))
                return matched_docs
                
        except Exception as e:
            logger.error(f"Search similar documents failed: {e}")
            # On Postgres, a failed statement leaves the transaction aborted -
            # any further query on this session raises InFailedSqlTransaction
            # until it's rolled back. Harmless no-op on SQLite.
            db.rollback()
            # Fallback to simple text search using LIKE if vector search fails
            keywords = query_text.split()[:3]
            like_filters = [InternalDoc.content_markdown.like(f"%{kw}%") for kw in keywords if len(kw) > 3]
            if like_filters:
                docs = db.query(InternalDoc).filter(*like_filters).limit(limit).all()
            else:
                docs = db.query(InternalDoc).limit(limit).all()
            return [(doc, 0.5) for doc in docs]
            
    @classmethod
    def register_document(cls, title: str, category: str, content: str, db: Session) -> InternalDoc:
        """Helper to create and save an internal document with computed vector embedding."""
        embedding = cls.get_embedding(content)
        
        # Serialize embedding for SQLite, or keep as list for SQLAlchemy/PostgreSQL pgvector
        db_embedding = json.dumps(embedding) if is_sqlite else embedding
        
        doc = InternalDoc(
            title=title,
            category=category,
            content_markdown=content,
            embedding=db_embedding
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
