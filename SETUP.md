# AI Butler — WhatsApp Morning Briefing

An AI agent that messages you every morning on WhatsApp with your daily tasks and meal plan, powered by Claude.

## How It Works

1. Reads `data/tasks.json` (your weekly tasks + one-off events)
2. Reads `data/meals.json` (your weekly meal plan)
3. Sends both to Claude (Opus 4.6) which writes a warm, personalised message
4. Sends the message to your WhatsApp via Twilio

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `TWILIO_ACCOUNT_SID` | https://console.twilio.com |
| `TWILIO_AUTH_TOKEN` | https://console.twilio.com |
| `TWILIO_WHATSAPP_FROM` | Twilio WhatsApp sandbox number (see below) |
| `WHATSAPP_TO` | Your WhatsApp number in `whatsapp:+XXXXXXXXXXX` format |
| `YOUR_NAME` | Your first name |
| `MORNING_HOUR` | Hour to send the message (24h, e.g. `7` for 7 AM) |
| `MORNING_MINUTE` | Minute offset (e.g. `30` for 7:30 AM) |

### 3. Set up Twilio WhatsApp Sandbox (free, for testing)

1. Sign up at https://www.twilio.com (free trial)
2. Go to **Messaging → Try it out → Send a WhatsApp message**
3. Follow the instructions to join the sandbox (send a code from your phone)
4. Your sandbox number is `whatsapp:+14155238886`
5. Set `TWILIO_WHATSAPP_FROM=whatsapp:+14155238886` in `.env`

For production, apply for a [WhatsApp-enabled Twilio number](https://www.twilio.com/whatsapp).

### 4. Personalise your data

Edit `data/tasks.json` — add your real weekly tasks and upcoming one-off events:

```json
{
  "weekly": {
    "monday": ["Standup at 9am", "Gym"],
    ...
  },
  "one_off": [
    { "date": "2026-04-15", "task": "Doctor appointment at 2pm" }
  ]
}
```

Edit `data/meals.json` — set your weekly meal plan:

```json
{
  "weekly": {
    "monday": {
      "breakfast": "Oats",
      "lunch": "Salad",
      "dinner": "Pasta",
      "snacks": ["Fruit", "Nuts"]
    },
    ...
  }
}
```

## Running

### Test once (send message now)

```bash
python butler.py
```

### Run the scheduler (sends every morning)

```bash
python scheduler.py
```

Keep it running with `screen`, `tmux`, or as a systemd service.

### Alternative: use cron

Instead of the scheduler, add a crontab entry:

```
0 7 * * * cd /path/to/ai-agents && python butler.py >> /tmp/butler.log 2>&1
```

## Project Structure

```
ai-agents/
├── butler.py          # Core agent logic
├── scheduler.py       # Daily scheduler
├── requirements.txt
├── .env.example
└── data/
    ├── tasks.json     # Your tasks (edit this)
    └── meals.json     # Your meal plan (edit this)
```
