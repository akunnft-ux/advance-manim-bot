import os
import sys

import requests


def notify_telegram(message: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        missing = [v for v in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID") if not os.environ.get(v)]
        print(f"[ERROR] Telegram notif gagal — env var tidak diset: {', '.join(missing)}. Set di GitHub Secrets.", file=sys.stderr)
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={"chat_id": chat_id, "text": message[:4096]}, timeout=10)
        if not resp.ok:
            print(f"[ERROR] Telegram API error {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] Telegram notify failed: {e}", file=sys.stderr)
