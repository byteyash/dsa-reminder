import os
import sys
from datetime import date, timedelta

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

    today = date.today()
    week_dates = {(today - timedelta(days=i)).isoformat() for i in range(7)}

    done_this_week = sum(
        1 for e in status.values()
        if e.get("status") == "done" and e.get("date") in week_dates
    )
    not_done_this_week = sum(
        1 for e in status.values()
        if e.get("status") == "not_done" and e.get("date") in week_dates
    )
    total_done = lib.count_done(status)
    streak = lib.compute_streak(status)

    text = (
        "Weekly DSA summary\n\n"
        f"This week: {done_this_week} done, {not_done_this_week} marked not done\n"
        f"Total progress: {total_done}/{len(questions)}\n"
        f"Current streak: {streak} day(s)"
    )

    try:
        result = lib.api_call(bot_token, "sendMessage", {"chat_id": chat_id, "text": text})
        print(result)
    except Exception as e:
        print(f"Failed to send weekly summary: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
