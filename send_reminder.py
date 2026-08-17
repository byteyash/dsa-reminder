import os
import sys
from datetime import date

import reminder_lib as lib


def main():
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    skip_weekends = os.environ.get("SKIP_WEEKENDS", "false").lower() == "true"
    per_day = int(os.environ.get("QUESTIONS_PER_DAY", "2"))

    if not bot_token or not chat_id:
        print("Missing BOT_TOKEN or CHAT_ID env vars")
        sys.exit(1)

    if skip_weekends and lib.is_weekend():
        print("Weekend and SKIP_WEEKENDS is true, not sending today")
        return

    base_dir = os.path.dirname(__file__)
    questions = lib.load_json(os.path.join(base_dir, "questions.json"), [])
    if not questions:
        print("questions.json is empty")
        sys.exit(1)

    status = lib.load_json(os.path.join(base_dir, "status.json"), {})

    idxs = lib.pick_daily_targets(questions, status, count=per_day)
    if not idxs:
        print("Nothing to send")
        return

    # remember today's picks so the evening nudge knows what to check on
    today_path = os.path.join(base_dir, "today.json")
    lib.save_json(today_path, {"date": date.today().isoformat(), "indices": idxs})

    try:
        for pos, idx in enumerate(idxs, start=1):
            text = lib.build_message(questions, status, idx, daily_position=pos, daily_total=len(idxs))
            result = lib.send_reminder_message(bot_token, chat_id, text, idx)
            print(result)
    except Exception as e:
        print(f"Failed to send reminder: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
