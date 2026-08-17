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

### 6. Test it
Go to the Actions tab in your repo -> "Daily DSA Reminder" -> "Run workflow"
(this is the `workflow_dispatch` trigger). You should get a Telegram message
within a few seconds.

### 7. Adjust the time
The cron `"30 1 * * *"` runs at 1:30 UTC = 7:00 AM IST. GitHub Actions cron
is always UTC, so subtract 5:30 from the IST time you want and put that in
the workflow file.

## Notes
- `START_DATE` in the workflow controls which day index you're on. Set it
  to today's date if you want to start from question 1 immediately.
- No servers, no cost. GitHub Actions free tier covers this easily
  (one run a day, a few seconds each).
- If you ever want it on WhatsApp instead, the script structure stays the
  same, only the API call to `sendMessage` changes to WhatsApp Cloud API
  once you've done the Meta business verification.
