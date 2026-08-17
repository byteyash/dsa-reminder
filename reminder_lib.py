import json
import os
import random
import re
import urllib.parse
import urllib.request
from datetime import date, timedelta


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def api_call(bot_token, method, params):
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def leetcode_slug(title):
    # Best-effort guess at a LeetCode URL slug. Not guaranteed to match
    # every title exactly (LeetCode's own display names sometimes differ),
    # so a search link is always included as a fallback.
    t = re.sub(r"\(.*?\)", "", title)
    t = t.strip().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def build_links(platform, title):
    query = urllib.parse.quote(f"{platform} {title}")
    search_link = f"https://www.google.com/search?q={query}"
    if platform.lower() == "leetcode":
        slug = leetcode_slug(title)
        direct_link = f"https://leetcode.com/problems/{slug}/"
        return direct_link, search_link
    return None, search_link


def compute_target_index(questions, status, base_index):
    """Start at base_index (from date math) and skip forward over anything
    already marked done, so a solved problem never gets sent again."""
    n = len(questions)
    if n == 0:
        return 0
    idx = base_index % n
    for _ in range(n):
        entry = status.get(str(idx))
        if not entry or entry.get("status") != "done":
            return idx
        idx = (idx + 1) % n
    return base_index % n  # everything is done, just repeat from base


def pick_daily_targets(questions, status, count=2):
    """Pick `count` random not-yet-done problems. If fewer than `count`
    remain unsolved, everything is considered fair game again (repeats
    allowed) rather than sending nothing."""
    n = len(questions)
    if n == 0:
        return []
    not_done = [i for i in range(n) if (status.get(str(i)) or {}).get("status") != "done"]
    pool = not_done if len(not_done) >= count else list(range(n))
    count = min(count, len(pool))
    return random.sample(pool, count)


def compute_streak(status):
    dates_done = {e.get("date") for e in status.values() if e.get("status") == "done"}
    streak = 0
    d = date.today()
    while d.isoformat() in dates_done:
        streak += 1
        d -= timedelta(days=1)
    return streak


def count_done(status):
    return sum(1 for e in status.values() if e.get("status") == "done")


def build_message(questions, status, idx, daily_position=None, daily_total=None):
    q = questions[idx]
    direct_link, search_link = build_links(q.get("platform", ""), q["title"])
    done_count = count_done(status)
    streak = compute_streak(status)

    header = f"DSA reminder - Problem {idx + 1}/{len(questions)}"
    if daily_position and daily_total:
        header = f"DSA reminder ({daily_position}/{daily_total} today) - Problem {idx + 1}/{len(questions)}"

    lines = [
        header,
        "",
        q["title"],
        f"Topic: {q.get('difficulty', 'N/A')}",
    ]
    note = q.get("note")
    if note:
        lines.append(f"Note: {note}")
    if direct_link:
        lines.append(f"Try: {direct_link}")
    lines.append(f"Search: {search_link}")
    lines.append("")
    lines.append(f"Progress: {done_count}/{len(questions)} done | Streak: {streak} day(s)")
    return "\n".join(lines)


def send_reminder_message(bot_token, chat_id, text, day_index, allow_buttons=True):
    params = {"chat_id": chat_id, "text": text}
    if allow_buttons:
        keyboard = {
            "inline_keyboard": [[
                {"text": "Done", "callback_data": f"done|{day_index}"},
                {"text": "Not done", "callback_data": f"skip|{day_index}"},
            ]]
        }
        params["reply_markup"] = json.dumps(keyboard)
    return api_call(bot_token, "sendMessage", params)


def is_weekend(d=None):
    d = d or date.today()
    return d.weekday() >= 5  # 5 = Saturday, 6 = Sunday
