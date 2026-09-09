import os
import json
import math
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./compliance_centras.db")

Base = declarative_base()

def sqlite_cosine_similarity(v1_str, v2_str):
    if not v1_str or not v2_str:
        return 0.0
    try:
        v1 = json.loads(v1_str) if isinstance(v1_str, str) else v1_str
        v2 = json.loads(v2_str) if isinstance(v2_str, str) else v2_str
        if not isinstance(v1, list) or not isinstance(v2, list):
            return 0.0
        if len(v1) != len(v2) or len(v1) == 0:
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)
    except Exception:
        return 0.0

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    
    @event.listens_for(engine, "connect")
    def register_sqlite_functions(dbapi_connection, connection_record):
        dbapi_connection.create_function("cosine_similarity", 2, sqlite_cosine_similarity)
else:
    # Production PostgreSQL engine with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
        pool_pre_ping=True
    )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DEFAULT_PROMPTS = {
    "system_prompt": (
        "Вы — Старший методолог и комплаенс-офицер страховой компании Республики Казахстан. "
        "Вы отлично знаете Гражданский кодекс РК, Закон 'О страховой деятельности', Закон 'О ПОД/ФТ' и постановления АРРФР."
    ),
    "legal_prompt": (
        "Проанализируй изменения между предыдущей и новой редакцией нормативного акта.\n\n"
        "Предыдущая редакция:\n```markdown\n{old_text}\n```\n\n"
        "Новая редакция:\n```markdown\n{new_text}\n```\n\n"
        "Подготовь подробный юридический анализ. Ответ верни в строгом формате JSON со следующими ключами:\n"
        "- what_changed (что конкретно изменилось)\n"
        "- requirements (какие новые регуляторные требования появились)\n"
        "- deadlines (сроки вступления в силу и дедлайны для выполнения)\n"
        "- risks (риски несоблюдения для страховой компании)\n"
        "- consequences (последствия для бизнес-процессов)\n"
        "Не используй markdown разметку вокруг JSON в ответе, верни чистый JSON-объект."
    ),
    "draft_prompt": (
        "Вы — Ведущий методолог страховой компании Республики Казахстан. "
        "На основе анализа изменений в законодательстве РК и предоставленных внутренних документов компании, подготовьте проекты необходимых изменений.\n\n"
        "АНАЛИЗ ИЗМЕНЕНИЙ ЗАКОНА:\n{analysis_str}\n\n"
        "СВЯЗАННЫЕ ВНУТРЕННИЕ РЕГЛАМЕНТЫ КОМПАНИИ:\n{related_docs}\n\n"
        "СТИЛИСТИЧЕСКИЕ И КОРПОРАТИВНЫЕ ПРАВИЛА:\n{style_guidelines}\n\n"
        "Пожалуйста, сформируйте ответ строго в JSON формате с ключами:\n"
        "- affected_departments: список затронутых департаментов (например, Методология, Юристы, Продажи, IT, Андеррайтинг, Урегулирование) с кратким обоснованием для каждого.\n"
        "- rules_changes: проект конкретных правок во внутренние правила (предыдущая редакция -> новая редакция).\n"
        "- memo: служебная записка о необходимости изменений.\n"
        "- board_letter: сопроводительное письмо для Правления компании.\n"
        "- board_directors_letter: письмо для Совета директоров.\n"
        "- implementation_plan: пошаговый план внедрения изменений (этап, сроки, ответственный).\n"
        "- checklist: комплаенс чек-лист для проверки внедрения.\n"
        "Возвращайте чистый JSON-объект без markdown разметки."
    ),
    "review_prompt": (
        "Вы — Независимый комплаенс-контролер. "
        "Проверьте подготовленные методологические проекты на корректность, полноту ссылок на законы и отсутствие логических ошибок.\n\n"
        "АНАЛИЗ ИЗМЕНЕНИЙ:\n{analysis_str}\n\n"
        "СГЕНЕРИРОВАННЫЕ ПРОЕКТЫ И ВЛИЯНИЕ:\n{draft_str}\n\n"
        "Сформируйте отчет проверки качества в формате JSON с ключами:\n"
        "- score: оценка от 1 до 100.\n"
        "- issues: список выявленных неточностей, пропущенных ссылок или несоответствий.\n"
        "- recommendations: предложения по доработке текста.\n"
        "- is_approved: логическое значение (true, если оценка >= 80, иначе false).\n"
        "Возвращайте только JSON-объект без markdown разметки."
    ),
    "audit_prompt": (
        "Проанализируй действующую редакцию нормативного акта ниже и оцени, насколько деятельность "
        "страховой компании потенциально соответствует ему в целом (плановая проверка — изменений "
        "текста закона с прошлой проверки не обнаружено).\n\n"
        "Действующая редакция:\n```markdown\n{current_text}\n```\n\n"
        "Подготовь подробный комплаенс-анализ. Ответ верни в строгом формате JSON со следующими ключами:\n"
        "- what_changed (кратко: что именно проверялось и что изменений в тексте закона нет)\n"
        "- requirements (ключевые регуляторные требования данного акта, которые компания обязана соблюдать)\n"
        "- deadlines (периодические или регулярные сроки/дедлайны, связанные с исполнением требований)\n"
        "- risks (риски несоблюдения для страховой компании, если требования не выполняются)\n"
        "- consequences (последствия для бизнес-процессов и рекомендации по проверке соответствия)\n"
        "Не используй markdown разметку вокруг JSON в ответе, верни чистый JSON-объект."
    ),
    "source_suggestion_prompt": (
        "Ты — старший методолог и комплаенс-офицер страховой компании Республики Казахстан.\n"
        "Изучи текст внутреннего документа компании ниже и определи, какие законы, постановления "
        "АРРФР и иные нормативно-правовые акты РК регулируют описанную деятельность и должны "
        "отслеживаться на предмет изменений.\n\n"
        "ТЕКСТ ДОКУМЕНТА:\n```markdown\n{content}\n```\n\n"
        "Для каждого найденного НПА укажи точное официальное название, официальную ссылку на "
        "актуальную редакцию (используй поиск, чтобы найти реальную страницу на adilet.zan.kz "
        "или официальном портале АРРФР/egov.kz — не придумывай ссылку, если не уверен, оставь "
        "url пустой строкой) и краткое обоснование, почему документ на него ссылается.\n\n"
        "Верни строго JSON-массив (без markdown разметки вокруг) вида:\n"
        "[{{\"title\": \"...\", \"url\": \"...\", \"reason\": \"...\", \"confidence\": \"high|medium|low\"}}]"
    ),
}


def init_db():
    if not is_sqlite:
        # For PostgreSQL, ensure pgvector extension is created
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
        except Exception:
            pass

    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass

    # Base.metadata.create_all only creates missing tables, not missing columns
    # on tables that already exist in production - task_type was added after
    # the tasks table was first deployed, so it needs an explicit migration.
    with engine.connect() as conn:
        try:
            if is_sqlite:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN task_type VARCHAR(20) DEFAULT 'change'"))
            else:
                conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS task_type VARCHAR(20) DEFAULT 'change'"))
            conn.commit()
        except Exception:
            conn.rollback()

    from app.models import User, Prompt
    from app.auth import get_password_hash
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@cic.kz").first()
        hashed_pw = get_password_hash("Holding22#")
        if not admin:
            try:
                new_admin = User(email="admin@cic.kz", hashed_password=hashed_pw)
                db.add(new_admin)
                db.commit()
            except Exception:
                db.rollback()
        else:
            try:
                admin.hashed_password = hashed_pw
                db.commit()
            except Exception:
                db.rollback()

        for key, content in DEFAULT_PROMPTS.items():
            existing = db.query(Prompt).filter(Prompt.key == key).first()
            if not existing:
                try:
                    db.add(Prompt(key=key, content=content, version=1))
                    db.commit()
                except Exception:
                    db.rollback()
    except Exception:
        db.rollback()
    finally:
        db.close()
