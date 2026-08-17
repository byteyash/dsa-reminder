# DSA Telegram Reminder

Sends you one DSA question a day on Telegram, for free, using GitHub Actions
as the scheduler (no server to run or pay for).

## Setup (about 10-15 minutes)

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
2. Push all files in this folder to it, keeping the `.github/workflows/`
   folder path exactly as is.

### 4. Add your secrets
In the repo: Settings -> Secrets and variables -> Actions -> New repository secret.
Add two secrets:
- `BOT_TOKEN` = the token from step 1
- `CHAT_ID` = the number from step 2

### 5. Fill in your questions
Edit `questions.json` and replace the sample 10 with your full list (your
300-problem tracker). Each entry needs `title`, `difficulty`, `link`.
The script sends them in order, one per day, and loops back to the start
once it reaches the end.

### 6. Allow Actions to write to the repo (needed for Done/Not done tracking)
Settings -> Actions -> General -> scroll to "Workflow permissions" ->
select "Read and write permissions" -> Save.
This lets the poller commit status updates back into the repo.

### 7. Test it
Go to the Actions tab in your repo -> "Daily DSA Reminder" -> "Run workflow"
(this is the `workflow_dispatch` trigger). You should get a Telegram message
within a few seconds, with "Done" / "Not done" buttons under it.

### 8. Adjust the time
The cron `"30 1 * * *"` runs at 1:30 UTC = 7:00 AM IST. GitHub Actions cron
is always UTC, so subtract 5:30 from the IST time you want and put that in
the workflow file.

## How the Done / Not done buttons work
Every reminder message has two buttons. Tapping one:
1. Instantly updates the message in Telegram (shows "Status: Done" or
   "Status: Not done", buttons disappear).
2. Gets picked up by a second workflow, "Poll Telegram Updates", which
   runs every 15 minutes, reads the button tap, and commits it into
   `status.json` in your repo (keyed by day index, e.g. `"0": {"status":
   "done", "date": "2026-08-19"}`).

That second workflow is what needs the write-permission step above, since
it pushes a commit. If you want status reflected faster, lower the `*/15`
in `.github/workflows/poll-updates.yml` to `*/5` (5 minutes is the
practical minimum for GitHub Actions cron).

You can also trigger it manually any time: Actions tab -> "Poll Telegram
Updates" -> "Run workflow".

## Notes
- `START_DATE` in the workflow controls which day index you're on. Set it
  to today's date if you want to start from question 1 immediately.
- No servers, no cost. GitHub Actions free tier covers this easily.
- `offset.json` just tracks which Telegram updates have already been
  processed, don't edit it by hand.
- If you ever want it on WhatsApp instead, the script structure stays the
  same, only the API call to `sendMessage` changes to WhatsApp Cloud API
  once you've done the Meta business verification.
