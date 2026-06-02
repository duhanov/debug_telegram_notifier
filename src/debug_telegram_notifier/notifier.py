import json
import os
import uuid
import urllib.error
import urllib.request


class DebugTelegramNotifier:
    """Best-effort sender for debug messages/files to Telegram."""

    def __init__(self) -> None:
        self.token = os.getenv("DEBUG_BOT_TOKEN", "").strip()
        self.chat_id = os.getenv("DEBUG_BOT_CHAT_ID", "").strip()
        self.app_name = os.getenv("DEBUG_BOT_APP_NAME", "").strip()
        self.enabled = bool(self.token and self.chat_id)

    def send_error(self, error_message: str, traceback_text: str = "") -> None:
        if not self.enabled:
            return

        base_message = error_message or "Unknown error"
        message_with_prefix = self._with_app_prefix(base_message)
        message_text = self._trim_text(message_with_prefix, 3000)
        self._send_message(message_text)

        if traceback_text:
            file_text = f"error_message:\n{message_with_prefix}\n\ntraceback:\n{traceback_text}"
            self._send_text_file(
                filename="error_traceback.txt",
                caption=self._trim_text(message_with_prefix, 900),
                file_text=file_text,
            )

    def _send_message(self, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = json.dumps(
            {
                "chat_id": self.chat_id,
                "text": text,
                "disable_web_page_preview": True,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url=url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        self._safe_urlopen(req)

    def _send_text_file(self, *, filename: str, caption: str, file_text: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendDocument"
        boundary = f"----cursor-boundary-{uuid.uuid4().hex}"
        body = self._build_multipart_body(
            boundary=boundary,
            fields={"chat_id": self.chat_id, "caption": caption},
            file_field="document",
            filename=filename,
            file_bytes=file_text.encode("utf-8"),
            content_type="text/plain; charset=utf-8",
        )
        req = urllib.request.Request(
            url=url,
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        self._safe_urlopen(req)

    @staticmethod
    def _build_multipart_body(
        *,
        boundary: str,
        fields: dict[str, str],
        file_field: str,
        filename: str,
        file_bytes: bytes,
        content_type: str,
    ) -> bytes:
        chunks: list[bytes] = []
        for key, value in fields.items():
            chunks.extend(
                [
                    f"--{boundary}\r\n".encode("utf-8"),
                    f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"),
                    value.encode("utf-8"),
                    b"\r\n",
                ]
            )

        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                (
                    f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'
                ).encode("utf-8"),
                f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
                file_bytes,
                b"\r\n",
                f"--{boundary}--\r\n".encode("utf-8"),
            ]
        )
        return b"".join(chunks)

    @staticmethod
    def _trim_text(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return f"{text[:limit]}... [truncated]"

    def _with_app_prefix(self, text: str) -> str:
        if not self.app_name:
            return text
        return f"[{self.app_name}] {text}"

    @staticmethod
    def _safe_urlopen(req: urllib.request.Request) -> None:
        try:
            with urllib.request.urlopen(req, timeout=6):
                pass
        except urllib.error.URLError:
            return
