import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date


def api_call(bot_token, method, params):
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("Missing BOT_TOKEN env var")
        sys.exit(1)

    base_dir = os.path.dirname(__file__)
    offset_path = os.path.join(base_dir, "offset.json")
    status_path = os.path.join(base_dir, "status.json")

    offset_data = load_json(offset_path, {"offset": 0})
    status = load_json(status_path, {})

    resp = api_call(bot_token, "getUpdates", {"offset": offset_data["offset"], "timeout": 0})
    if not resp.get("ok"):
        print("getUpdates failed:", resp)
        sys.exit(1)

    updates = resp["result"]
    changed = False

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
            ack_text = "Marked done"
            suffix = "\n\nStatus: Done"
        elif action == "skip":
            status[day_index] = {"status": "not_done", "date": date.today().isoformat()}
            ack_text = "Marked not done"
            suffix = "\n\nStatus: Not done"
        else:
            continue

        changed = True

        api_call(bot_token, "answerCallbackQuery", {
            "callback_query_id": cq["id"],
            "text": ack_text,
        })

        api_call(bot_token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": original_text + suffix,
            "reply_markup": json.dumps({"inline_keyboard": []}),
        })

    save_json(offset_path, offset_data)
    if changed:
        save_json(status_path, status)

    print(f"Processed {len(updates)} update(s), status changed={changed}")


if __name__ == "__main__":
    main()
