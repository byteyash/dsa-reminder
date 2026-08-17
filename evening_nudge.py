import os
import sys
from datetime import date

import reminder_lib as lib


def main():
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not bot_token or not chat_id:
        print("Missing BOT_TOKEN or CHAT_ID env vars")
        sys.exit(1)

    base_dir = os.path.dirname(__file__)
    questions = lib.load_json(os.path.join(base_dir, "questions.json"), [])
    status = lib.load_json(os.path.join(base_dir, "status.json"), {})
    today_data = lib.load_json(os.path.join(base_dir, "today.json"), {})

    if not questions or today_data.get("date") != date.today().isoformat():
        print("No picks recorded for today yet, nothing to nudge about")
        return

    idxs = today_data.get("indices", [])
    pending = [i for i in idxs if (status.get(str(i)) or {}).get("status") != "done"]

    if not pending:
        print("Everything for today is already done, no nudge needed")
        return

    try:
        for idx in pending:
            pos = idxs.index(idx) + 1
            text = "Still pending today:\n\n" + lib.build_message(
                questions, status, idx, daily_position=pos, daily_total=len(idxs)
            )
            result = lib.send_reminder_message(bot_token, chat_id, text, idx)
            print(result)
    except Exception as e:
        print(f"Failed to send nudge: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
