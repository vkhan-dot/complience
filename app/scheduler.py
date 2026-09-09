import asyncio
import logging
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Source, SourceVersion, Task
from app.agents.monitoring import MonitoringAgent
from app.agents.notifications import NotificationService

logger = logging.getLogger(__name__)


class ComplianceScheduler:
    """
    Background asynchronous scheduler for automated periodic regulatory checks.
    Runs in the background of the FastAPI application lifespan.
    """

    def __init__(self, check_interval_seconds: int = 60):
        self.check_interval_seconds = check_interval_seconds
        self._running = False
        self._task: asyncio.Task | None = None
        self.last_run: datetime | None = None
        self.total_checks_run = 0
        self.executor = ThreadPoolExecutor(max_workers=3)

    def is_running(self) -> bool:
        return self._running and self._task is not None and not self._task.done()

    def start(self, change_pipeline_fn=None, audit_pipeline_fn=None):
        """Starts the background monitoring loop."""
        if self._running:
            return
        self._running = True
        self.change_pipeline_fn = change_pipeline_fn
        self.audit_pipeline_fn = audit_pipeline_fn
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"ComplianceScheduler started. Interval: {self.check_interval_seconds}s")

    async def stop(self):
        """Stops the background monitoring loop cleanly."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.executor.shutdown(wait=False)
        logger.info("ComplianceScheduler stopped.")

    async def _run_loop(self):
        # Initial slight delay to let application start completely
        await asyncio.sleep(2)
        while self._running:
            try:
                await asyncio.to_thread(self.check_overdue_sources)
            except Exception as e:
                logger.error(f"Error in ComplianceScheduler run loop: {e}")
            
            try:
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                break

    @staticmethod
    def is_due(last_checked: datetime | None, check_interval_hours: float, now: datetime | None = None) -> bool:
        """Determines if a source is due for an automated compliance audit."""
        if not last_checked:
            return True
        if now is None:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
        hours_passed = (now - last_checked).total_seconds() / 3600.0
        return hours_passed >= check_interval_hours

    def check_overdue_sources(self, db: Session = None) -> dict:
        """
        Scans database for active sources that are due for checking based on their check_interval_hours.
        Returns summary of checks performed.
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        self.last_run = now
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        summary = {"checked": 0, "changes_found": 0, "audits_run": 0, "errors": 0}

        try:
            active_sources = db.query(Source).filter(Source.is_active == True).all()

            for source in active_sources:
                if self.is_due(source.last_checked, source.check_interval_hours, now):
                    logger.info(f"Scheduled check triggered for source #{source.id} ({source.title})")
                    summary["checked"] += 1
                    self.total_checks_run += 1

                    res = MonitoringAgent.run_check(source.id, db)
                    status = res.get("status")

                    if status == "changed" and res.get("task_id"):
                        summary["changes_found"] += 1
                        task_id = res["task_id"]
                        
                        # Create Notification
                        NotificationService.create_notification(
                            title=f"🚨 Изменения в {source.title}",
                            message=f"Обнаружена новая редакция (версия #{res.get('version')}). Запущен автоматический юридический анализ и подготовка проектов регламентов.",
                            type="change_detected",
                            severity="high",
                            link_url=f"#tasks",
                            db=db
                        )

                        # Run change pipeline in thread
                        if self.change_pipeline_fn:
                            self.executor.submit(self.change_pipeline_fn, task_id)

                    elif status in ("unchanged", "cosmetic_only"):
                        existing_pending = db.query(Task).filter(
                            Task.source_id == source.id,
                            Task.status == "Pending"
                        ).first()

                        if not existing_pending:
                            latest_version = db.query(SourceVersion).filter(
                                SourceVersion.source_id == source.id
                            ).order_by(SourceVersion.version_num.desc()).first()

                            if latest_version:
                                summary["audits_run"] += 1
                                audit_task = Task(
                                    source_id=source.id,
                                    old_version_id=latest_version.id,
                                    new_version_id=latest_version.id,
                                    task_type="audit",
                                    diff_html=(
                                        "<div style='padding:20px;text-align:center;'>"
                                        "Текст закона не изменился. Ниже — результаты плановой проверки "
                                        "соответствия текущей редакции.</div>"
                                    ),
                                    status="Pending"
                                )
                                db.add(audit_task)
                                db.commit()
                                db.refresh(audit_task)

                                if self.audit_pipeline_fn:
                                    self.executor.submit(self.audit_pipeline_fn, audit_task.id)


                    elif status == "error":
                        summary["errors"] += 1
                        NotificationService.create_notification(
                            title=f"❌ Ошибка мониторинга {source.title}",
                            message=f"Не удалось проверить источник: {res.get('error')}",
                            type="error",
                            severity="high",
                            link_url="#monitoring",
                            db=db
                        )

        except Exception as e:
            logger.error(f"Error during scheduled source check: {e}")
            summary["errors"] += 1
        finally:
            if close_db:
                db.close()

        return summary


    def get_status(self) -> dict:
        next_in = self.check_interval_seconds
        if self.last_run:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            elapsed = (now - self.last_run).total_seconds()
            next_in = max(0, int(self.check_interval_seconds - elapsed))

        return {
            "is_running": self.is_running(),
            "interval_seconds": self.check_interval_seconds,
            "last_run": self.last_run.strftime("%Y-%m-%d %H:%M:%S") if self.last_run else None,
            "next_run_in_seconds": next_in,
            "total_checks_run": self.total_checks_run
        }

# Global singleton instance
scheduler = ComplianceScheduler(check_interval_seconds=60)

