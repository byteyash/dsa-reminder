# DSA Telegram Reminder

Sends you one DSA question a day on Telegram, for free, using GitHub Actions
as the scheduler (no server to run or pay for). Includes Done/Not done
tracking, streaks, an evening nudge, a weekly summary, and optional
solution backups.

## Setup (about 15-20 minutes)

### 1. Create the bot
1. Open Telegram, search for `@BotFather`, start a chat.
2. Send `/newbot`, give it a name and a username ending in `bot`.
3. BotFather replies with a token like `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`.
   Save it, this is your `BOT_TOKEN`.

### 2. Get your chat ID
1. Send any message to your new bot (e.g. "hi").
2. In a browser, open:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find `"chat":{"id": ...}` in the response. That number is your `CHAT_ID`.

### 3. Push this to GitHub
1. Create a new repo (can be private) on GitHub.
2. Upload all files in this folder, keeping the `.github/workflows/`
   folder path exactly as is.

### 4. Add your secrets
Settings -> Secrets and variables -> Actions -> New repository secret.
Add two:
- `BOT_TOKEN` = the token from step 1
- `CHAT_ID` = the number from step 2

### 5. Fill in your questions
`questions.json` already has your full list. Each entry has `title`,
`difficulty` (used as a topic label), `link`, `platform`, and an optional
`note` field you can fill in per problem if you want a hint to show up
in the message. Two are picked at random each day; change
`QUESTIONS_PER_DAY` in `daily-reminder.yml` to send a different number.

### 6. Allow Actions to write to the repo
Settings -> Actions -> General -> "Workflow permissions" -> select
"Read and write permissions" -> Save.
This is required for the poller to commit status updates and saved
solutions back into the repo.

### 7. Test it
Actions tab -> "Daily DSA Reminder" -> "Run workflow". You should get a
Telegram message within a few seconds, with Done/Not done buttons and a
progress/streak line under it.

### 8. Adjust the times
All schedules run in UTC. IST is UTC+5:30, so subtract 5:30 from the IST
time you want:
- `daily-reminder.yml`: `"30 1 * * *"` = 7:00 AM IST
- `evening-nudge.yml`: `"30 14 * * *"` = 8:00 PM IST
- `weekly-summary.yml`: `"30 15 * * 0"` = 9:00 PM IST, Sundays
- `poll-updates.yml`: runs every 15 minutes, lower `*/15` to `*/5` for
  faster status updates (5 min is the practical floor for GitHub Actions)

## What each workflow does

**Daily DSA Reminder** - picks 2 random not-yet-done problems each day
(each arrives as its own message with its own Done/Not done buttons) and
records the picks in `today.json` so the evening nudge knows what to
check on. Once fewer than 2 unsolved problems remain, it starts allowing
repeats rather than sending nothing. Set `SKIP_WEEKENDS: "true"` or change
`QUESTIONS_PER_DAY` in its env block to adjust either behavior.

**Poll Telegram Updates** - runs every 15 min, picks up button taps,
updates the message in Telegram, and commits the result to `status.json`.
When you tap Done, it also asks you to reply with your solution code
(or reply "skip"); if you send code, it's committed to `solutions/`.

**Evening Nudge** - checks late in the day whether either of today's two
picks (from `today.json`) is still unsolved, and resends a follow-up for
each one that is.

**Weekly Summary** - every Sunday, tallies the week's done/not-done count,
total progress, and current streak, and sends it as one message.

## Notes
- Selection is random each day, not sequential, so `START_DATE` is no
  longer used.
- `today.json` records which problems were picked for the current day;
  it's what the evening nudge reads. Don't edit it by hand.
- Streak = consecutive days with at least one problem marked done.
- LeetCode links are best-effort guesses at the URL slug from the title;
  a Google search link is always included as a fallback in case the
  direct link doesn't resolve.
- `offset.json` and `awaiting.json` are internal state, don't edit by hand.
- No servers, no cost. All of this fits well inside GitHub Actions' free
  tier for a personal repo.
- If you ever want it on WhatsApp instead, the script structure stays the
  same, only the `sendMessage` call changes to the WhatsApp Cloud API
  once you've done the Meta business verification.
