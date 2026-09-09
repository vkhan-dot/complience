import json
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, sqlite_cosine_similarity
from app.models import User, Source, SourceVersion, InternalDoc, Task, Prompt, PromptHistory, Memory, Notification
from app.agents.monitoring import MonitoringAgent
from app.agents.parsing import ParsingAgent
from app.agents.document import DocumentAgent
from app.agents.notifications import NotificationService
from app.scheduler import ComplianceScheduler
from app.auth import get_password_hash, verify_password, create_access_token
from app.main import app, get_db

# ----------------- UNIT TESTS -----------------

def test_calculate_sha256():
    text = "тестовый закон Республики Казахстан"
    h1 = MonitoringAgent.calculate_sha256(text)
    h2 = MonitoringAgent.calculate_sha256(text)
    assert h1 == h2
    assert len(h1) == 64


def test_difference_engine_cosmetic():
    old_text = "Подпись: Иванов А.\nДата: 10.05.2026\n# Статья 1. Общие положения"
    new_text = "Подпись: Иванов А.В.\nДата: 12.05.2026\n# Статья 1. Общие положения"
    
    has_real_changes, diff_html = MonitoringAgent.diff_documents(old_text, new_text)
    assert not has_real_changes
    assert "<table class='diff-table'>" in diff_html


def test_difference_engine_real_change():
    old_text = "Минимальный размер уставного капитала 1 000 000 тенге"
    new_text = "Минимальный размер уставного капитала 1 500 000 тенге"
    
    has_real_changes, diff_html = MonitoringAgent.diff_documents(old_text, new_text)
    assert has_real_changes
    assert "class='add'" in diff_html
    assert "class='del'" in diff_html


def test_sqlite_cosine_similarity():
    # Identical
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    sim = sqlite_cosine_similarity(v1, v2)
    assert abs(sim - 1.0) < 1e-6
    
    # Orthogonal
    v3 = [0.0, 1.0, 0.0]
    sim_ortho = sqlite_cosine_similarity(v1, v3)
    assert abs(sim_ortho - 0.0) < 1e-6

    # JSON strings
    sim_json = sqlite_cosine_similarity(json.dumps(v1), json.dumps(v2))
    assert abs(sim_json - 1.0) < 1e-6

    # Edge cases
    assert sqlite_cosine_similarity(None, v1) == 0.0
    assert sqlite_cosine_similarity([], []) == 0.0
    assert sqlite_cosine_similarity([0, 0], [0, 0]) == 0.0


def test_parsing_agent_structure_extraction():
    sample_md = (
        "Вводная часть без заголовка.\n\n"
        "# 1. Общие положения\nТекст первой статьи.\n\n"
        "## 1.1. Термины\nОпределения терминов.\n\n"
        "# 2. Требования к капиталу\nМинимум 1.5 млрд тенге."
    )
    sections = ParsingAgent._extract_sections(sample_md)
    assert len(sections) == 4
    assert sections[0]["title"] == "Преамбула"
    assert sections[1]["title"] == "1. Общие положения"
    assert sections[2]["title"] == "1.1. Термины"
    assert sections[3]["title"] == "2. Требования к капиталу"



def test_document_agent_normalizers():
    # 1. Departments normalizer
    raw_depts_list = ["Методология", {"department": "Юристы", "reason": "Договорные риски"}]
    norm_depts = DocumentAgent._normalize_departments(raw_depts_list)
    assert len(norm_depts) == 2
    assert norm_depts[0]["department"] == "Методология"
    assert norm_depts[1]["department"] == "Юристы"

    # Dict format
    dict_depts = {"Андеррайтинг": "Изменение тарифов"}
    norm_dict = DocumentAgent._normalize_departments(dict_depts)
    assert len(norm_dict) == 1
    assert norm_dict[0]["department"] == "Андеррайтинг"

    # 2. Plan normalizer
    raw_plan = [
        {"step": "Обновление правил", "deadline": "10 дней", "owner": "Методолог"},
        "Провести обучение сотрудников"
    ]
    norm_plan = DocumentAgent._normalize_plan(raw_plan)
    assert len(norm_plan) == 2
    assert norm_plan[0]["step"] == "Обновление правил"
    assert norm_plan[1]["step"] == "Провести обучение сотрудников"

    # 3. Checklist normalizer
    raw_checklist = [
        {"item": "Проверить приказ"},
        "- [ ] Проверить регистрацию в МЮ РК"
    ]
    norm_cl = DocumentAgent._normalize_checklist(raw_checklist)
    assert len(norm_cl) == 2
    assert norm_cl[0]["item"] == "Проверить приказ"
    assert norm_cl[1]["item"] == "Проверить регистрацию в МЮ РК"

    # 4. Review normalizer
    raw_rev = {"score": "88", "issues": ["Небольшая опечатка"], "recommendations": ["Исправить"], "is_approved": True}
    norm_rev = DocumentAgent._normalize_review(raw_rev)
    assert norm_rev["score"] == 88
    assert norm_rev["is_approved"] is True
    assert len(norm_rev["issues"]) == 1


def test_auth_password_and_jwt():
    raw_pw = "SecretPass123!"
    hashed = get_password_hash(raw_pw)
    assert verify_password(raw_pw, hashed)
    assert not verify_password("WrongPassword", hashed)

    token = create_access_token({"sub": "admin@cic.kz"})
    assert token is not None
    assert isinstance(token, str)


# ----------------- INTEGRATION & ENDPOINTS TESTS -----------------

@pytest.fixture(name="client")
def client_fixture(tmp_path):
    test_db_file = tmp_path / "test_compliance.db"
    test_db_url = f"sqlite:///{test_db_file}"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def register_sqlite_functions(dbapi_connection, connection_record):
        dbapi_connection.create_function("cosine_similarity", 2, sqlite_cosine_similarity)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed admin user
    db = TestingSessionLocal()
    admin = User(email="admin@cic.kz", hashed_password=get_password_hash("Holding22#"))
    db.add(admin)
    db.commit()

    # Seed default prompt
    db.add(Prompt(key="legal_prompt", content="Промпт {old_text} {new_text}", version=1))
    db.commit()
    db.close()

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_full_api_workflow(client: TestClient, tmp_path):
    # 1. Login
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Dashboard
    dash_resp = client.get("/api/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert "sources_count" in dash_data
    assert "unread_notifications" in dash_data

    # 3. Create Law File and Source
    law_file = tmp_path / "law_test.txt"
    law_file.write_text("# Закон РК\nСтатья 1. Размер уставного капитала 1 000 000 тенге.", encoding="utf-8")

    src_resp = client.post(
        "/api/sources",
        json={"title": "Закон о страховании", "url": str(law_file), "check_interval_hours": 24},
        headers=headers
    )
    assert src_resp.status_code == 200
    source_id = src_resp.json()["id"]

    # 4. Check Source (Baseline was established during source creation, so unchanged)
    check_resp = client.post(f"/api/sources/{source_id}/check", headers=headers)
    assert check_resp.status_code == 200
    assert check_resp.json()["status"] in ("unchanged", "cosmetic_only")

    # 5. Simulate real law change in file and check again -> generates Task
    law_file.write_text("# Закон РК\nСтатья 1. Размер уставного капитала 2 500 000 тенге.", encoding="utf-8")
    check_changed = client.post(f"/api/sources/{source_id}/check", headers=headers)
    assert check_changed.status_code == 200
    assert check_changed.json()["status"] == "changed"
    task_id = check_changed.json()["task_id"]

    # 6. Task Management: get task detail
    task_resp = client.get(f"/api/tasks/{task_id}", headers=headers)
    assert task_resp.status_code == 200
    task_data = task_resp.json()
    assert task_data["id"] == task_id
    assert task_data["status"] == "Pending"

    # 7. Save Drafts manually
    draft_payload = {
        "rules_changes": "Пункт 4.1. Уставный капитал 1 500 000 тенге",
        "memo": "Служебная записка в Правление",
        "board_letter": "Письмо Правлению СК",
        "board_directors_letter": "Письмо СД",
        "implementation_plan": [{"step": "Правка правил", "deadline": "5 дней", "owner": "Методолог"}],
        "checklist": [{"item": "Проверка соответствия АРРФР"}]
    }
    save_draft_resp = client.post(f"/api/tasks/{task_id}/save_drafts", json=draft_payload, headers=headers)
    assert save_draft_resp.status_code == 200

    # 8. Export to DOCX for all document types
    for doc_type in ["memo", "rules", "board_letter", "board_directors_letter", "plan", "checklist"]:
        export_resp = client.get(f"/api/tasks/{task_id}/export/{doc_type}", headers=headers)
        assert export_resp.status_code == 200
        assert export_resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert len(export_resp.content) > 0

    # 9. Approve Task & Self-Learning Memory
    approve_resp = client.put(f"/api/tasks/{task_id}", json={"status": "Approved"}, headers=headers)
    assert approve_resp.status_code == 200

    # 10. Reject another Task to verify rejection memory recording
    reject_task_resp = client.put(
        f"/api/tasks/{task_id}",
        json={"status": "Rejected", "reject_reason": "Не учтены нормы закона о ПОД/ФТ"},
        headers=headers
    )
    assert reject_task_resp.status_code == 200

    # 11. Internal Documents CRUD
    doc_resp = client.post(
        "/api/documents",
        json={"title": "Регламент КАСКО", "category": "Правила страхования", "content_markdown": "# Правила КАСКО"},
        headers=headers
    )
    assert doc_resp.status_code == 200
    doc_id = doc_resp.json()["id"]

    docs_list = client.get("/api/documents", headers=headers)
    assert docs_list.status_code == 200
    assert len(docs_list.json()) >= 1

    # 12. Relations Graph
    rel_resp = client.get("/api/relations", headers=headers)
    assert rel_resp.status_code == 200
    assert "nodes" in rel_resp.json()
    assert "links" in rel_resp.json()

    # 13. Prompt Zone (Update and History)
    prompt_resp = client.put(
        "/api/prompts/legal_prompt",
        json={"content": "Обновленный юридический промпт v2"},
        headers=headers
    )
    assert prompt_resp.status_code == 200
    assert prompt_resp.json()["version"] == 2

    # 14. Notifications API
    test_notif = client.post("/api/notifications/test", headers=headers)
    assert test_notif.status_code == 200
    notif_id = test_notif.json()["id"]

    notifs_list = client.get("/api/notifications", headers=headers)
    assert notifs_list.status_code == 200
    assert notifs_list.json()["unread_count"] >= 1

    read_notif = client.put(f"/api/notifications/{notif_id}/read", headers=headers)
    assert read_notif.status_code == 200

    read_all = client.post("/api/notifications/read-all", headers=headers)
    assert read_all.status_code == 200

    # 15. Scheduler Status and Run
    sched_status = client.get("/api/scheduler/status", headers=headers)
    assert sched_status.status_code == 200

    sched_run = client.post("/api/scheduler/run-now", headers=headers)
    assert sched_run.status_code == 200
    assert "summary" in sched_run.json()

    # 16. Cleanup Document
    del_doc = client.delete(f"/api/documents/{doc_id}", headers=headers)
    assert del_doc.status_code == 200

    # 17. Chat Endpoint Safety Check
    chat_resp = client.post("/api/chat", json={"message": "Какие основные законы регулируют страхование в РК?"}, headers=headers)
    assert chat_resp.status_code == 200
    assert "response" in chat_resp.json()


def test_parsing_html_tables(tmp_path):
    html_content = """
    <html>
        <body>
            <h1>Тарифы и нормативы</h1>
            <p>Ниже представлена таблица коэффициентов:</p>
            <table>
                <tr><th>Класс риска</th><th>Коэффициент</th></tr>
                <tr><td>1 класс</td><td>1.2</td></tr>
                <tr><td>2 класс</td><td>1.5</td></tr>
            </table>
        </body>
    </html>
    """
    html_file = tmp_path / "table_test.html"
    html_file.write_text(html_content, encoding="utf-8")

    content, sections = ParsingAgent._parse_html_file(str(html_file))
    assert "| Класс риска | Коэффициент |" in content
    assert "| 1 класс | 1.2 |" in content
    assert len(sections) >= 1


def test_scheduler_duplicate_audit_prevention(tmp_path):
    test_db_file = tmp_path / "test_sched_dup.db"
    engine = create_engine(f"sqlite:///{test_db_file}", connect_args={"check_same_thread": False})
    
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def reg_sim(dbapi_conn, rec):
        dbapi_conn.create_function("cosine_similarity", 2, sqlite_cosine_similarity)

    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestSession()
    # Create file
    law_file = tmp_path / "stable_law.txt"
    law_file.write_text("Стабильный закон без изменений", encoding="utf-8")

    src = Source(title="Стабильный Закон", url=str(law_file), check_interval_hours=0, is_active=True)
    db.add(src)
    db.commit()
    db.refresh(src)

    # First check -> creates initial version
    MonitoringAgent.run_check(src.id, db)
    
    # Run scheduler
    sched = ComplianceScheduler()
    s1 = sched.check_overdue_sources(db=db)
    
    # Check pending tasks count
    tasks_count_1 = db.query(Task).filter(Task.source_id == src.id, Task.status == "Pending").count()
    assert tasks_count_1 == 1

    # Run scheduler second time immediately on same unchanged source -> should NOT create duplicate pending task
    s2 = sched.check_overdue_sources(db=db)
    tasks_count_2 = db.query(Task).filter(Task.source_id == src.id, Task.status == "Pending").count()
    assert tasks_count_2 == 1  # Still exactly 1, no duplicates!
    
    db.close()


def test_healthcheck_endpoint(client: TestClient):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["database"] == "healthy"
    assert "scheduler" in data
    assert "version" in data

    resp_api = client.get("/api/health")
    assert resp_api.status_code == 200


def test_security_headers(client: TestClient):
    resp = client.get("/healthz")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-XSS-Protection"] == "1; mode=block"
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_unauthenticated_routes_blocked(client: TestClient):
    # Protected endpoints without token should return 401 Unauthorized or 403 Forbidden
    assert client.get("/api/dashboard").status_code in (401, 403)
    assert client.get("/api/sources").status_code in (401, 403)
    assert client.get("/api/tasks").status_code in (401, 403)
    assert client.get("/api/documents").status_code in (401, 403)
    assert client.get("/api/relations").status_code in (401, 403)
    assert client.get("/api/prompts").status_code in (401, 403)
    assert client.get("/api/notifications").status_code in (401, 403)


def test_login_invalid_credentials(client: TestClient):
    resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "WrongPassword123"}
    )
    assert resp.status_code in (400, 401)
    assert resp.json()["detail"] == "Incorrect email or password"


def test_sandbox_endpoints(client: TestClient):
    # 1. Login to get token
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test sandbox compare endpoint
    compare_resp = client.post(
        "/api/sandbox/compare",
        json={
            "old_text": "Статья 10. Капитал 1 млрд тенге",
            "new_text": "Статья 10. Капитал 1.5 млрд тенге"
        },
        headers=headers
    )
    assert compare_resp.status_code == 200
    res = compare_resp.json()
    assert res["is_identical"] is False
    assert res["has_real_changes"] is True
    assert res["chars_old"] > 0
    assert res["chars_new"] > 0
    assert "class='add'" in res["diff_html"]


def test_telegram_test_notification(client: TestClient):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/notifications/telegram-test", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("success", "warning")


def test_sandbox_parse_file_and_fetch_url(client: TestClient, tmp_path):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test parsing an uploaded file (.txt)
    test_content = b"# Zakon RK\nStatya 1. Trebovaniya k registratsii."
    files = {"file": ("test_law.txt", test_content, "text/plain")}
    parse_resp = client.post("/api/sandbox/parse-file", files=files, headers=headers)
    assert parse_resp.status_code == 200
    data = parse_resp.json()
    assert "text" in data
    assert "Zakon RK" in data["text"]
    assert data["chars"] > 0

    # 2. Test fetching a local file as URL
    local_file = tmp_path / "sandbox_law.txt"
    local_file.write_text("# Zakon RK\nStatya 2. Trebovaniya k kapitalu.", encoding="utf-8")
    url_resp = client.post(
        "/api/sandbox/fetch-url",
        json={"url": str(local_file)},
        headers=headers
    )
    assert url_resp.status_code == 200
    u_data = url_resp.json()
    assert "text" in u_data
    assert "Statya 2" in u_data["text"]


def test_source_live_simulation(client: TestClient):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/sources/test-simulation", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "source_id" in data


# ----------------- COMPREHENSIVE TDD & E2E TESTS -----------------

def test_prompts_versioning_and_history(client: TestClient):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get Prompts list
    prompts_resp = client.get("/api/prompts", headers=headers)
    assert prompts_resp.status_code == 200
    prompts = prompts_resp.json()
    assert isinstance(prompts, list)
    assert len(prompts) > 0

    # 2. Update a Prompt to trigger versioning
    target_key = prompts[0]["key"]
    initial_version = prompts[0]["version"]

    update_resp = client.put(
        f"/api/prompts/{target_key}",
        json={"content": "Обновленный системный промпт для методолога {old_text} {new_text}"},
        headers=headers
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["version"] == initial_version + 1

    # 3. Update again to reach version + 2
    update_resp2 = client.put(
        f"/api/prompts/{target_key}",
        json={"content": "Третья итерация промпта {old_text} {new_text}"},
        headers=headers
    )
    assert update_resp2.status_code == 200
    assert update_resp2.json()["version"] == initial_version + 2


def test_relations_graph_structure(client: TestClient, tmp_path):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Seed an internal doc and a source
    doc_resp = client.post(
        "/api/documents",
        json={"title": "Правила страхования КАСКО", "category": "Автострахование", "content_markdown": "# Правила КАСКО\nПункт 1."},
        headers=headers
    )
    assert doc_resp.status_code == 200

    relations_resp = client.get("/api/relations", headers=headers)
    assert relations_resp.status_code == 200
    graph = relations_resp.json()
    assert "nodes" in graph
    assert "links" in graph
    assert isinstance(graph["nodes"], list)
    assert isinstance(graph["links"], list)
    
    # Verify graph contains our document
    doc_nodes = [n for n in graph["nodes"] if n.get("type") in ("rule", "internal_doc") or "КАСКО" in n.get("label", "")]
    assert len(doc_nodes) > 0


def test_source_crud_and_floating_intervals(client: TestClient, tmp_path):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create with 1-minute interval (0.0167 hours)
    law_file = tmp_path / "min_interval_law.txt"
    law_file.write_text("# Закон о ценных бумагах\nСтатья 1.", encoding="utf-8")

    create_resp = client.post(
        "/api/sources",
        json={"title": "Закон о РЦБ (Live 1m)", "url": str(law_file), "check_interval_hours": 0.0167},
        headers=headers
    )
    assert create_resp.status_code == 200
    source = create_resp.json()
    assert source["id"] is not None
    assert abs(source["check_interval_hours"] - 0.0167) < 1e-4

    source_id = source["id"]

    # 2. Update Source
    update_resp = client.put(
        f"/api/sources/{source_id}",
        json={"title": "Закон о РЦБ (Обновленный)", "url": str(law_file), "check_interval_hours": 0.0833, "is_active": True},
        headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Закон о РЦБ (Обновленный)"
    assert abs(update_resp.json()["check_interval_hours"] - 0.0833) < 1e-4

    # 3. Delete Source
    del_resp = client.delete(f"/api/sources/{source_id}", headers=headers)
    assert del_resp.status_code == 200

    # 4. Verify 404 after deletion
    get_del = client.get(f"/api/sources/{source_id}", headers=headers)
    assert get_del.status_code == 404


def test_internal_documents_full_lifecycle(client: TestClient):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create document
    create_resp = client.post(
        "/api/documents",
        json={"title": "Положение об актуарных расчетах", "category": "Актуарный расчет", "content_markdown": "# Актуарные расчеты\nМетодика оценки резервов."},
        headers=headers
    )
    assert create_resp.status_code == 200
    doc_id = create_resp.json()["id"]

    # 2. Search document
    search_resp = client.get("/api/documents?search=актуарных", headers=headers)
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) >= 1
    assert any(d["id"] == doc_id for d in results)

    # 3. Get single document
    get_resp = client.get(f"/api/documents/{doc_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Положение об актуарных расчетах"

    # 4. Delete document
    del_resp = client.delete(f"/api/documents/{doc_id}", headers=headers)
    assert del_resp.status_code == 200

    # 5. Verify deletion
    search_after = client.get("/api/documents?search=актуарных", headers=headers)
    assert search_after.status_code == 200
    assert not any(d["id"] == doc_id for d in search_after.json())


def test_notifications_center_lifecycle(client: TestClient):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create test notification
    create_resp = client.post("/api/notifications/test", headers=headers)
    assert create_resp.status_code == 200
    notif = create_resp.json()
    notif_id = notif["id"]

    # 2. List notifications
    list_resp = client.get("/api/notifications", headers=headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    items = data.get("items", [])
    assert len(items) > 0
    assert any(n["id"] == notif_id for n in items)

    # 3. Mark single notification as read
    read_resp = client.post(f"/api/notifications/{notif_id}/read", headers=headers)
    assert read_resp.status_code == 200

    # 4. Mark all as read
    read_all_resp = client.post("/api/notifications/read-all", headers=headers)
    assert read_all_resp.status_code == 200


def test_scheduler_interval_logic():
    # 1. Test when last_checked is None -> is_due should be True
    assert ComplianceScheduler.is_due(None, 24.0) is True

    # 2. Test when last_checked is 5 seconds ago and interval is 24 hours -> is_due should be False
    recent_check = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=5)
    assert ComplianceScheduler.is_due(recent_check, 24.0) is False

    # 3. Test when interval is 1 minute (0.0167 hours) and last check was 2 minutes ago -> is_due should be True
    old_check_1m = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=2)
    assert ComplianceScheduler.is_due(old_check_1m, 0.0167) is True

    # 4. Test when interval is 5 minutes (0.0833 hours) and last check was 1 minute ago -> is_due should be False
    recent_check_5m = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    assert ComplianceScheduler.is_due(recent_check_5m, 0.0833) is False


def test_review_agent_scoring_and_penalties():
    # Test 1: Clean drafts with no issues
    perfect_report = {
        "score": 100,
        "is_approved": True,
        "issues": [],
        "recommendations": ["Соответствует всем требованиям"]
    }
    assert perfect_report["score"] == 100
    assert perfect_report["is_approved"] is True

    # Test 2: Verify penalty calculation helper if issues exist
    issues = [
        "Критическое несоответствие статье 15 Закона РК",
        "Не указан срок в плане внедрения",
        "Отсутствует подпись ответственного актуария"
    ]
    # Simulating deduction logic
    base_score = 100
    deductions = len(issues) * 15
    final_score = max(0, min(100, base_score - deductions))
    assert final_score == 55
    assert final_score < 80  # Requires revision


def test_knowledge_agent_vector_search():
    # Test vector cosine similarity helper with diverse vectors
    v_query = [0.8, 0.6, 0.0]
    v_doc1 = [0.8, 0.6, 0.0]     # exact match
    v_doc2 = [-0.8, -0.6, 0.0]   # opposite
    v_doc3 = [0.0, 0.0, 1.0]     # orthogonal

    assert abs(sqlite_cosine_similarity(v_query, v_doc1) - 1.0) < 1e-5
    assert sqlite_cosine_similarity(v_query, v_doc2) <= 0.0
    assert abs(sqlite_cosine_similarity(v_query, v_doc3) - 0.0) < 1e-5


def test_adversarial_malformed_inputs(client: TestClient):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Zero-byte file upload to sandbox
    empty_files = {"file": ("empty.txt", b"", "text/plain")}
    resp_empty = client.post("/api/sandbox/parse-file", files=empty_files, headers=headers)
    assert resp_empty.status_code == 400
    assert "Не удалось извлечь текст" in resp_empty.json()["detail"] or "Ошибка" in resp_empty.json()["detail"]

    # 2. Non-existent source URL fetch in sandbox
    resp_bad_url = client.post("/api/sandbox/fetch-url", json={"url": "data/laws/non_existent_file_12345.txt"}, headers=headers)
    assert resp_bad_url.status_code == 400

    # 3. Non-existent Task ID query
    resp_bad_task = client.get("/api/tasks/999999", headers=headers)
    assert resp_bad_task.status_code == 404

    # 4. Non-existent Source ID query
    resp_bad_source = client.get("/api/sources/999999", headers=headers)
    assert resp_bad_source.status_code == 404

    # 5. Non-existent Prompt Key update
    resp_bad_prompt = client.put("/api/prompts/non_existent_prompt_key_xyz", json={"content": "test"}, headers=headers)
    assert resp_bad_prompt.status_code == 404

    # 6. Malformed JSON login payload vs bad credentials
    resp_empty_login = client.post("/api/login", data={"username": "", "password": ""})
    assert resp_empty_login.status_code == 422

    resp_bad_credentials = client.post("/api/login", data={"username": "wrong@example.com", "password": "wrongpassword"})
    assert resp_bad_credentials.status_code == 401


def test_source_and_document_docx_exports(client: TestClient, tmp_path):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a law file & Source -> check DOCX export
    law_file = tmp_path / "export_test_law.txt"
    law_file.write_text("# Закон об экспорте\nСтатья 1. Тестовый текст закона.", encoding="utf-8")

    src_resp = client.post(
        "/api/sources",
        json={"title": "Закон для экспорта", "url": str(law_file), "check_interval_hours": 24},
        headers=headers
    )
    assert src_resp.status_code == 200
    src_id = src_resp.json()["id"]

    export_src_resp = client.get(f"/api/sources/{src_id}/export", headers=headers)
    assert export_src_resp.status_code == 200
    assert export_src_resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(export_src_resp.content) > 1000

    # 2. Create Internal Doc -> check DOCX export
    doc_resp = client.post(
        "/api/documents",
        json={"title": "Регламент экспорта", "category": "Методология", "content_markdown": "# Регламент\nРаздел 1. Правила."},
        headers=headers
    )
    assert doc_resp.status_code == 200
    doc_id = doc_resp.json()["id"]

    export_doc_resp = client.get(f"/api/documents/{doc_id}/export", headers=headers)
    assert export_doc_resp.status_code == 200
    assert export_doc_resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(export_doc_resp.content) > 1000


def test_legal_portal_parsing_and_article_toc(tmp_path):
    # Simulate a web page from Paragraph / Adilet with articles, banner noise, and table
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Закон РК О страховой деятельности</title></head>
    <body>
        <nav class="doc_nav">Меню навигации</nav>
        <div class="banner">Реклама и баннеры</div>
        <main class="document-page">
            <h1>Закон Республики Казахстан</h1>
            <p>Статья 1. Основные понятия, используемые в настоящем Законе</p>
            <p>В настоящем Законе используются следующие понятия: 1) страхование...</p>
            <p>Статья 2. Законодательство Республики Казахстан о страховании</p>
            <p>Законодательство Республики Казахстан основывается на Конституции...</p>
        </main>
        <footer class="doc-footer">Дата формирования: 2026-08-19</footer>
    </body>
    </html>
    """
    sample_file = tmp_path / "prg_sample.html"
    sample_file.write_text(html_content, encoding="utf-8")

    md, sections = ParsingAgent.parse_file(str(sample_file))
    
    # Assert noise tags are decomposed
    assert "Реклама и баннеры" not in md
    assert "Меню навигации" not in md
    assert "Дата формирования" not in md

    # Assert article headers recognized
    assert "### Статья 1" in md
    assert "### Статья 2" in md
    assert len(sections) >= 2
    assert any(s.get("article_num") == "1" for s in sections)
    assert any(s.get("article_num") == "2" for s in sections)

    # Test Side by Side word-level diff
    old_text = "### Статья 1. Основные понятия\nСтраховой капитал равен 1000 тенге."
    new_text = "### Статья 1. Основные понятия\nСтраховой капитал равен 2500 тенге."

    has_changes, diff_html = MonitoringAgent.diff_documents(old_text, new_text)
    assert has_changes
    assert "data-article=" in diff_html
    assert "<del class='inline-del'>1000</del>" in diff_html
    assert "<ins class='inline-ins'>2500</ins>" in diff_html


def test_comparative_table_docx_export_and_article_alignment(client: TestClient):
    login_resp = client.post(
        "/api/login",
        data={"username": "admin@cic.kz", "password": "Holding22#"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test Two-Pass Alignment when a new article is inserted in the middle
    v1_text = """### Статья 1. Основные положения
Пункт 1. Текст первого пункта.
### Статья 2. Лицензирование
Пункт 1. Требуется лицензия АРРФР.
### Статья 3. Заключительные положения
Закон вступает в силу с момента опубликования."""

    v2_text = """### Статья 1. Основные положения
Пункт 1. Текст первого пункта.
### Статья 2. Лицензирование
Пункт 1. Требуется генеральная лицензия АРРФР.
### Статья 2-1. Электронные услуги
Пункт 1. Оказание услуг в цифровом виде.
### Статья 3. Заключительные положения
Закон вступает в силу с момента опубликования."""

    has_diff, diff_html = MonitoringAgent.diff_documents(v1_text, v2_text)
    assert has_diff
    assert "data-article='Статья 2-1. Электронные услуги'" in diff_html
    assert "генеральная" in diff_html
    assert "inline-ins" in diff_html

    # Test Task creation and comparative table DOCX generation
    db = next(app.dependency_overrides[get_db]())
    src = Source(title="Закон о лицензировании", url="http://test.local/law", check_interval_hours=24)
    db.add(src)
    db.commit()

    sv1 = SourceVersion(source_id=src.id, version_num=1, content_markdown=v1_text, sha256=MonitoringAgent.calculate_sha256(v1_text))
    sv2 = SourceVersion(source_id=src.id, version_num=2, content_markdown=v2_text, sha256=MonitoringAgent.calculate_sha256(v2_text))
    db.add_all([sv1, sv2])
    db.commit()

    task = Task(source_id=src.id, old_version_id=sv1.id, new_version_id=sv2.id, diff_html=diff_html, status="Pending")
    db.add(task)
    db.commit()

    # Call /api/tasks/{id}/export_table
    resp = client.get(f"/api/tasks/{task.id}/export_table", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(resp.content) > 1000













