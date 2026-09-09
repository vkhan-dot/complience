import os
import json
import logging
import urllib.request
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Notification
from app.database import SessionLocal

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Manages in-app compliance alerts, audit notifications, and external webhook / Telegram dispatches.
    """

    @classmethod
    def create_notification(
        cls,
        title: str,
        message: str,
        type: str = "info",
        severity: str = "normal",
        link_url: str = None,
        db: Session = None
    ) -> Notification:
        """
        Creates and persists an in-app notification.
        Also triggers external webhook / Telegram dispatch if configured.
        """
        close_session = False
        if db is None:
            db = SessionLocal()
            close_session = True

        try:
            notification = Notification(
                title=title,
                message=message,
                type=type,
                severity=severity,
                link_url=link_url,
                is_read=False,
                created_at=datetime.now(timezone.utc)
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)

            # Fire and forget webhook/telegram dispatch if configured
            try:
                cls._dispatch_external(title, message, type, severity, link_url)
            except Exception as ex:
                logger.warning(f"External notification dispatch error: {ex}")

            return notification
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            if db:
                db.rollback()
            raise
        finally:
            if close_session:
                db.close()

    @classmethod
    def get_notifications(cls, db: Session, limit: int = 30, unread_only: bool = False):
        query = db.query(Notification)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @classmethod
    def get_unread_count(cls, db: Session) -> int:
        return db.query(Notification).filter(Notification.is_read == False).count()

    @classmethod
    def mark_as_read(cls, notification_id: int, db: Session) -> bool:
        n = db.query(Notification).filter(Notification.id == notification_id).first()
        if not n:
            return False
        n.is_read = True
        db.commit()
        return True

    @classmethod
    def mark_all_as_read(cls, db: Session) -> int:
        count = db.query(Notification).filter(Notification.is_read == False).update({"is_read": True})
        db.commit()
        return count

    @classmethod
    def _dispatch_external(cls, title: str, message: str, type: str, severity: str, link_url: str = None):
        """Sends notifications to configured external webhooks or Telegram."""
        webhook_url = os.getenv("WEBHOOK_URL")
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        payload = {
            "title": title,
            "message": message,
            "type": type,
            "severity": severity,
            "link_url": link_url,
            "timestamp": datetime.now(timezone.utc).isoformat()

        }

        # 1. Custom HTTP Webhook
        if webhook_url:
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    webhook_url,
                    data=data,
                    headers={"Content-Type": "application/json", "User-Agent": "ComplianceCentras/1.0"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    logger.info(f"Webhook notification dispatched to {webhook_url}: HTTP {resp.status}")
            except Exception as e:
                logger.warning(f"Failed to dispatch webhook notification: {e}")

        # 2. Telegram Bot Alert
        if telegram_token and telegram_chat_id:
            try:
                icon_map = {
                    "change_detected": "🚨 ИЗМЕНЕНИЕ ЗАКОНОДАТЕЛЬСТВА",
                    "audit_completed": "📋 ПЛАНОВАЯ ПРОВЕРКА",
                    "quality_warning": "⚠️ ТРЕБУЕТСЯ ДОРАБОТКА",
                    "error": "❌ ОШИБКА МОНИТОРИНГА",
                    "info": "ℹ️ ИНФОРМАЦИЯ"
                }
                header = icon_map.get(type, "📢 УВЕДОМЛЕНИЕ")
                tg_text = f"<b>{header}</b>\n\n<b>{title}</b>\n{message}"
                if link_url:
                    tg_text += f"\n\n🔗 Ссылка: {link_url}"

                tg_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                tg_payload = json.dumps({
                    "chat_id": telegram_chat_id,
                    "text": tg_text,
                    "parse_mode": "HTML"
                }).encode("utf-8")
                req = urllib.request.Request(
                    tg_url,
                    data=tg_payload,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    logger.info("Telegram notification dispatched successfully.")
            except Exception as e:
                logger.warning(f"Failed to dispatch Telegram notification: {e}")
