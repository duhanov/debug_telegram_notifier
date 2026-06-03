import logging
import traceback

from .notifier import DebugTelegramNotifier

# Не слать в debug-бот шум от сканеров / неверного Host.
_SKIP_LOGGERS = ("django.security.DisallowedHost",)


def _record_should_skip(record: logging.LogRecord) -> bool:
    # print(f"record.name: {record.name}")
    if record.name in _SKIP_LOGGERS:
        print(f"SKIP LOG Error: {record.name}")
        return True

    return False


class TelegramDebugHandler(logging.Handler):
    """Collects log data and delegates delivery to debug Telegram notifier."""

    def __init__(self) -> None:
        super().__init__(level=logging.ERROR)
        self.notifier = DebugTelegramNotifier()

    def emit(self, record: logging.LogRecord) -> None:
        if not self.notifier.enabled or _record_should_skip(record):
            return

        try:
            error_message, traceback_text = self._build_payload(record)
            print(f"error_message: {error_message}")
            print(f"traceback_text: {traceback_text}")
            self.notifier.send_error(error_message, traceback_text)
        except Exception:
            # Never break main flow because of debug notification failures.
            self.handleError(record)

    def _build_payload(self, record: logging.LogRecord) -> tuple[str, str]:
        traceback_text = ""
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            traceback_text = "".join(traceback.format_exception(*record.exc_info))
            error_message = f"{exc_type.__name__}: {exc_value}"
            return error_message, traceback_text

        # Fallback for log records without exception info.
        error_message = record.getMessage()
        return error_message, traceback_text
