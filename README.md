# debug-telegram-notifier

Package for Django (and any Python project using `logging`) that forwards **ERROR**-level log records to a dedicated Telegram debug bot.

1. Install package (already configured in this repo via editable dependency):

```bash
pip install -e ./debug_telegram_notifier
```

2. Add env vars:

```env
DEBUG_BOT_TOKEN=123456:ABCDEF...
DEBUG_BOT_CHAT_ID=123456789
DEBUG_BOT_APP_NAME=caption-prod
```

3. Register logging handler in `settings.py`:

```python
LOGGING = {
    # ...
    "handlers": {
        "debug_telegram": {
            "class": "debug_telegram_notifier.logging.TelegramDebugHandler",
            "level": "ERROR",
        },
    },
    "root": {
        "handlers": ["debug_telegram"],
        "level": "ERROR",
    },
}
```

## Message format

- Telegram message contains only `error_message`.
- If traceback exists, it is sent as `error_traceback.txt`.
- The traceback file contains both:
  - `error_message`
  - `traceback`
- If `DEBUG_BOT_APP_NAME` is set, message starts with `[DEBUG_BOT_APP_NAME]`.

