import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime


def load_questions(path):
    with open(path, "r") as f:
        return json.load(f)


def main():
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    start_date_str = os.environ.get("START_DATE", "2026-06-01")

    if not bot_token or not chat_id:
        print("Missing BOT_TOKEN or CHAT_ID env vars")
        sys.exit(1)

    base_dir = os.path.dirname(__file__)
    questions = load_questions(os.path.join(base_dir, "questions.json"))
    if not questions:
        print("questions.json is empty")
        sys.exit(1)

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    today = date.today()
    day_index = (today - start_date).days

    if day_index < 0:
        print("Start date is in the future, nothing to send yet")
        return

    # loop back to day 1 once the list runs out, so it never just stops
    day_index = day_index % len(questions)
    q = questions[day_index]

    text = (
        f"DSA reminder - Day {day_index + 1}\n\n"
        f"{q['title']}\n"
        f"Topic: {q.get('difficulty', 'N/A')}\n"
        f"{q.get('link', '')}"
    )

    keyboard = {
        "inline_keyboard": [[
            {"text": "Done", "callback_data": f"done|{day_index}"},
            {"text": "Not done", "callback_data": f"skip|{day_index}"},
        ]]
    }

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "reply_markup": json.dumps(keyboard),
    }).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        result = resp.read().decode()
        print(result)


if __name__ == "__main__":
    main()
