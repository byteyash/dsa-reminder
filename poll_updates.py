import json
import os
import sys
from datetime import date

import reminder_lib as lib


def safe_call(bot_token, method, params, label=""):
    """Call the Telegram API but never let a single failed call (expired
    callback, already-edited message, etc.) crash the whole run."""
    try:
        result = lib.api_call(bot_token, method, params)
        if not result.get("ok"):
            print(f"Telegram API call failed ({label or method}): {result}")
        return result
    except Exception as e:
        print(f"Telegram API call raised ({label or method}): {e}")
        return None


def main():
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("Missing BOT_TOKEN env var")
        sys.exit(1)

    base_dir = os.path.dirname(__file__)
    offset_path = os.path.join(base_dir, "offset.json")
    status_path = os.path.join(base_dir, "status.json")

    offset_data = lib.load_json(offset_path, {"offset": 0})
    status = lib.load_json(status_path, {})

    resp = safe_call(bot_token, "getUpdates", {"offset": offset_data["offset"], "timeout": 0}, "getUpdates")
    if not resp or not resp.get("ok"):
        print("getUpdates failed, nothing more to do this run")
        sys.exit(1)

    updates = resp["result"]
    status_changed = False

    for upd in updates:
        offset_data["offset"] = upd["update_id"] + 1

        cq = upd.get("callback_query")
        if not cq:
            continue

        data = cq.get("data", "")
        if "|" not in data:
            continue

        action, day_index = data.split("|", 1)
        chat_id = cq["message"]["chat"]["id"]
        message_id = cq["message"]["message_id"]
        original_text = cq["message"].get("text", "")

        if action == "done":
            status[day_index] = {"status": "done", "date": date.today().isoformat()}
            status_changed = True
            ack_text, suffix = "Marked done", "\n\nStatus: Done"
        elif action == "skip":
            status[day_index] = {"status": "not_done", "date": date.today().isoformat()}
            status_changed = True
            ack_text, suffix = "Marked not done", "\n\nStatus: Not done"
        else:
            continue

        safe_call(bot_token, "answerCallbackQuery",
                  {"callback_query_id": cq["id"], "text": ack_text}, "answerCallbackQuery")
        safe_call(bot_token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": original_text + suffix,
            "reply_markup": json.dumps({"inline_keyboard": []}),
        }, "editMessageText")

    lib.save_json(offset_path, offset_data)
    if status_changed:
        lib.save_json(status_path, status)

    print(f"Processed {len(updates)} update(s). status_changed={status_changed}")


if __name__ == "__main__":
    main()
