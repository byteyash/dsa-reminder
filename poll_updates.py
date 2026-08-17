import json
import os
import re
import sys
from datetime import date

import reminder_lib as lib


def slugify(text):
    t = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    return t.strip("-")[:60] or "problem"


def main():
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        print("Missing BOT_TOKEN env var")
        sys.exit(1)

    base_dir = os.path.dirname(__file__)
    offset_path = os.path.join(base_dir, "offset.json")
    status_path = os.path.join(base_dir, "status.json")
    awaiting_path = os.path.join(base_dir, "awaiting.json")
    questions_path = os.path.join(base_dir, "questions.json")

    offset_data = lib.load_json(offset_path, {"offset": 0})
    status = lib.load_json(status_path, {})
    awaiting = lib.load_json(awaiting_path, {})
    questions = lib.load_json(questions_path, [])

    resp = lib.api_call(bot_token, "getUpdates", {"offset": offset_data["offset"], "timeout": 0})
    if not resp.get("ok"):
        print("getUpdates failed:", resp)
        sys.exit(1)

    updates = resp["result"]
    status_changed = False
    awaiting_changed = False
    saved = []

    for upd in updates:
        offset_data["offset"] = upd["update_id"] + 1

        cq = upd.get("callback_query")
        if cq:
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
                lib.api_call(bot_token, "answerCallbackQuery",
                             {"callback_query_id": cq["id"], "text": "Marked done"})
                lib.api_call(bot_token, "editMessageText", {
                    "chat_id": chat_id, "message_id": message_id,
                    "text": original_text + "\n\nStatus: Done",
                    "reply_markup": json.dumps({"inline_keyboard": []}),
                })
                lib.api_call(bot_token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": "Nice. Reply with your solution code and I'll save it to the repo, or reply 'skip'.",
                })
                awaiting = {"day_index": day_index, "chat_id": chat_id}
                awaiting_changed = True

            elif action == "skip":
                status[day_index] = {"status": "not_done", "date": date.today().isoformat()}
                status_changed = True
                lib.api_call(bot_token, "answerCallbackQuery",
                             {"callback_query_id": cq["id"], "text": "Marked not done"})
                lib.api_call(bot_token, "editMessageText", {
                    "chat_id": chat_id, "message_id": message_id,
                    "text": original_text + "\n\nStatus: Not done",
                    "reply_markup": json.dumps({"inline_keyboard": []}),
                })
            continue

        msg = upd.get("message")
        if msg and awaiting.get("day_index") is not None:
            text = msg.get("text", "")
            chat_id = msg["chat"]["id"]
            if str(chat_id) != str(awaiting.get("chat_id")):
                continue

            day_index = awaiting["day_index"]
            if text.strip().lower() == "skip":
                lib.api_call(bot_token, "sendMessage",
                             {"chat_id": chat_id, "text": "Skipped saving a solution."})
            else:
                idx = int(day_index)
                title = questions[idx]["title"] if idx < len(questions) else "problem"
                fname = f"{idx:04d}-{slugify(title)}.txt"
                sol_dir = os.path.join(base_dir, "solutions")
                os.makedirs(sol_dir, exist_ok=True)
                with open(os.path.join(sol_dir, fname), "w") as f:
                    f.write(text)
                saved.append(fname)
                lib.api_call(bot_token, "sendMessage",
                             {"chat_id": chat_id, "text": f"Saved to solutions/{fname}"})

            awaiting = {}
            awaiting_changed = True

    lib.save_json(offset_path, offset_data)
    if status_changed:
        lib.save_json(status_path, status)
    if awaiting_changed:
        lib.save_json(awaiting_path, awaiting)

    print(f"Processed {len(updates)} update(s). status_changed={status_changed} saved={saved}")


if __name__ == "__main__":
    main()
