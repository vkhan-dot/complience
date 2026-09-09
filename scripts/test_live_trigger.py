"""
Live Trigger & 1-Minute Scheduler Simulation Script.
Simulates a live modification of a law file, registers/updates the source with a 1-minute interval,
and verifies automated change detection and hash recalculation.
"""
import os
import sys
import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Source
from app.agents.monitoring import MonitoringAgent


def run_simulation():
    print("=" * 60)
    print("[*] Centras Compliance: Запуск Live-симулятора 1-минутного триггера")
    print("=" * 60)

    init_db()
    db: Session = SessionLocal()

    try:
        laws_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "laws"))
        os.makedirs(laws_dir, exist_ok=True)
        test_file = os.path.join(laws_dir, "test_live_law.txt")

        current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
        rand_amount = 1500000 + int(datetime.datetime.now().timestamp()) % 500000

        content = (
            f"# Закон РК 'О страховании и комплаенс-контроле' (Live-симуляция)\n\n"
            f"Статья 5. Минимальный гарантийный фонд страховой организации.\n"
            f"1. Размер фонда устанавливается в размере {rand_amount:,} тенге.\n"
            f"2. Требование обновлено в реальном времени в {current_time_str}.\n"
            f"3. Страховые компании обязаны исполнить норматив в течение 3 рабочих дней.\n"
        )

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[1/3] Записана новая редакция в {test_file}")
        print(f"      Размер фонда: {rand_amount:,} тенге, Время: {current_time_str}")

        src = db.query(Source).filter(Source.title == "Тестовый закон (Live-симуляция)").first()
        if not src:
            src = Source(
                title="Тестовый закон (Live-симуляция)",
                url=test_file,
                check_interval_hours=0.0167,
                is_active=True
            )
            db.add(src)
            db.commit()
            db.refresh(src)
            print(f"[2/3] Создан новый источник #{src.id} с интервалом проверки 1 мин.")
        else:
            src.url = test_file
            src.check_interval_hours = 0.0167
            src.is_active = True
            db.commit()
            print(f"[2/3] Обновлен источник #{src.id} с интервалом проверки 1 мин.")

        print(f"[3/3] Запуск MonitoringAgent.run_check(source_id={src.id})...")
        res = MonitoringAgent.run_check(src.id, db)
        print(f"[OK] Результат проверки:")
        print(f"   - Статус: {res.get('status')}")
        print(f"   - SHA-256: {res.get('sha256', src.last_sha256)}")
        if res.get("task_id"):
            print(f"   - Создана задача аудита ID: #{res.get('task_id')}")

        print("=" * 60)
        print("[OK] Симуляция успешно завершена! Шедулер продолжит опрос каждую 1 минуту.")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    run_simulation()
