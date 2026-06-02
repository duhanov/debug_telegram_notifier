import logging
import traceback

from .notifier import DebugTelegramNotifier


class TelegramDebugHandler(logging.Handler):
    """Collects log data and delegates delivery to debug Telegram notifier."""

    def __init__(self) -> None:
        super().__init__(level=logging.ERROR)
        self.notifier = DebugTelegramNotifier()

    def emit(self, record: logging.LogRecord) -> None:
        if not self.notifier.enabled:
            return

        try:
            error_message, traceback_text = self._build_payload(record)
            self.notifier.send_error(error_message, traceback_text)
        except Exception:
            # Never break main flow because of debug notification failures.
            self.handleError(record)

    def _build_payload(self, record: logging.LogRecord) -> tuple[str, str]:
        logger_name = record.name or "root"
        level = record.levelname
        message = record.getMessage()
        error_message = f"[{level}] {logger_name}: {message}"

        traceback_text = ""
        if record.exc_info:
            traceback_text = "".join(traceback.format_exception(*record.exc_info))
        return error_message, traceback_text
