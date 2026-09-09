import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base, is_sqlite

# Define the Embedding column type dynamically based on pgvector availability
EmbeddingType = Text
if not is_sqlite:
    try:
        from pgvector.sqlalchemy import Vector
        EmbeddingType = Vector(768)  # gemini-embedding-001, pinned to 768 dims via output_dimensionality
    except ImportError:
        EmbeddingType = Text

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)  # URL or local path
    check_interval_hours = Column(Float, default=24.0)
    last_sha256 = Column(String(64), nullable=True)
    last_checked = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    versions = relationship("SourceVersion", back_populates="source", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="source", cascade="all, delete-orphan")


class SourceVersion(Base):
    __tablename__ = "source_versions"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    version_num = Column(Integer, nullable=False)
    sha256 = Column(String(64), nullable=False)
    content_markdown = Column(Text, nullable=False)
    parsed_structure = Column(JSON, nullable=True)  # Section map
    created_at = Column(DateTime, default=utcnow)

    source = relationship("Source", back_populates="versions")


class InternalDoc(Base):
    __tablename__ = "internal_docs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # e.g., Rules, Instructions, Contracts, IT
    content_markdown = Column(Text, nullable=False)
    embedding = Column(EmbeddingType, nullable=True)  # Vector or serialized JSON string
    created_at = Column(DateTime, default=utcnow)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    old_version_id = Column(Integer, ForeignKey("source_versions.id", ondelete="SET NULL"), nullable=True)
    new_version_id = Column(Integer, ForeignKey("source_versions.id", ondelete="SET NULL"), nullable=True)
    task_type = Column(String(20), default="change")  # change (diff detected) or audit (periodic compliance review, no text change)
    status = Column(String(50), default="Pending")  # Pending, Approved, Rejected
    reject_reason = Column(Text, nullable=True)
    
    # Store agents output
    diff_html = Column(Text, nullable=True)  # HTML colorized side-by-side diff
    analysis_json = Column(JSON, nullable=True)  # {what_changed, risks, consequences, departments}
    draft_json = Column(JSON, nullable=True)  # {rules_changes, memo, board_letter, checklist}
    
    created_at = Column(DateTime, default=utcnow)

    source = relationship("Source", back_populates="tasks")
    old_version = relationship("SourceVersion", foreign_keys=[old_version_id])
    new_version = relationship("SourceVersion", foreign_keys=[new_version_id])


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=utcnow)

    history = relationship("PromptHistory", back_populates="prompt", cascade="all, delete-orphan")


class PromptHistory(Base):
    __tablename__ = "prompt_histories"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    prompt = relationship("Prompt", back_populates="history")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # style, decision, terminology, methodology, regulatory
    content_text = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")  # change_detected, audit_completed, quality_warning, error, info
    severity = Column(String(20), default="normal")  # normal, high, critical
    link_url = Column(String(255), nullable=True)  # URL or tab hash
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=utcnow, index=True)


