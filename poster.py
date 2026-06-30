import json
import os

import requests

from config import MODE_FILE, get_env
from compliance import compliance_check


def _load_mode() -> dict:
    try:
        with open(MODE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"mode": "telegram", "last_update_id": 0}


def _save_mode(mode_data: dict):
    os.makedirs(os.path.dirname(MODE_FILE), exist_ok=True)
    with open(MODE_FILE, "w") as f:
        json.dump(mode_data, f, indent=2)


def check_mode() -> str:
    mode_data = _load_mode()
    current_mode = mode_data.get("mode", "telegram")
    last_id = mode_data.get("last_update_id", 0)

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return current_mode

    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params={"offset": last_id + 1, "timeout": 5},
        )
        if resp.ok:
            for upd in resp.json().get("result", []):
                uid = upd["update_id"]
                if uid > last_id:
                    last_id = uid
                    text = (upd.get("message") or {}).get("text", "").strip().lower()
                    if text == "/mode facebook":
                        current_mode = "facebook"
                        requests.post(
                            f"https://api.telegram.org/bot{token}/sendMessage",
                            json={"chat_id": chat_id, "text": "\u2705 Mode berubah ke FACEBOOK"},
                            timeout=10,
                        )
                    elif text == "/mode telegram":
                        current_mode = "telegram"
                        requests.post(
                            f"https://api.telegram.org/bot{token}/sendMessage",
                            json={"chat_id": chat_id, "text": "\u2705 Mode berubah ke TELEGRAM"},
                            timeout=10,
                        )
    except Exception:
        pass

    _save_mode({"mode": current_mode, "last_update_id": last_id})
    return current_mode


def check_fb_token() -> tuple:
    token = os.environ.get("FB_ACCESS_TOKEN")
    page_id = os.environ.get("FB_PAGE_ID")
    if not token or not page_id:
        return False, "FB credentials not set"

    try:
        resp = requests.get(
            f"https://graph.facebook.com/v22.0/{page_id}",
            params={"access_token": token, "fields": "id,name"},
            timeout=15,
        )
        if resp.status_code == 200:
            return True, None
        elif resp.status_code == 401:
            return False, "BLOCKED_TOKEN_EXPIRED: Facebook token expired"
        else:
            return False, f"Token check failed: {resp.status_code}"
    except requests.RequestException as e:
        return False, f"Token check error: {e}"


def post_to_facebook(video_path: str, caption: str) -> dict:
    token = get_env("FB_ACCESS_TOKEN")
    page_id = get_env("FB_PAGE_ID")

    valid, err = check_fb_token()
    if not valid:
        from notifier import notify_telegram
        notify_telegram(f"[BLOCKED] {err}")
        raise PermissionError(err)

    compliance_check(caption)

    url = f"https://graph.facebook.com/v22.0/{page_id}/videos"
    with open(video_path, "rb") as f:
        files = {"source": (os.path.basename(video_path), f, "video/mp4")}
        data = {"description": caption, "access_token": token}
        resp = requests.post(url, files=files, data=data, timeout=120)

    if resp.status_code == 200:
        result = resp.json()
        print(f"[OK] Posted to Facebook. Post ID: {result.get('id')}")
        return result
    elif resp.status_code == 401:
        from notifier import notify_telegram
        notify_telegram("[BLOCKED] Token expired during upload")
        raise PermissionError("Token expired")
    elif resp.status_code == 429:
        raise RuntimeError("Rate limited")
    else:
        body = resp.text[:500]
        raise RuntimeError(f"Facebook upload failed: {resp.status_code} {body}")


def send_telegram(video_path: str, caption: str):
    token = get_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_env("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendVideo"
    with open(video_path, "rb") as f:
        files = {"video": f}
        data = {"chat_id": chat_id, "caption": caption[:1024], "supports_streaming": True}
        resp = requests.post(url, files=files, data=data, timeout=120)

    if not resp.ok:
        raise RuntimeError(f"Telegram sendVideo failed: {resp.status_code} {resp.text[:200]}")
    msg_id = resp.json()["result"]["message_id"]
    print(f"[OK] Sent to Telegram. Message ID: {msg_id}")
