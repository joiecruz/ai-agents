"""
AI Butler — Morning briefing agent.

Reads today's tasks and meal plan, uses Claude to generate a warm
personalised morning message, and sends it via WhatsApp (Twilio).
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from twilio.rest import Client as TwilioClient

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_json(filename: str) -> dict:
    with open(DATA_DIR / filename) as f:
        return json.load(f)


def get_todays_tasks(tasks_data: dict, today: date) -> list[str]:
    weekday = today.strftime("%A").lower()
    tasks = list(tasks_data["weekly"].get(weekday, []))

    today_str = today.isoformat()
    for entry in tasks_data.get("one_off", []):
        if entry["date"] == today_str:
            tasks.append(entry["task"])

    return tasks


def get_todays_meals(meals_data: dict, today: date) -> dict:
    weekday = today.strftime("%A").lower()
    return meals_data["weekly"].get(weekday, {})


# ---------------------------------------------------------------------------
# Claude — generate the morning briefing
# ---------------------------------------------------------------------------

def generate_briefing(name: str, today: date, tasks: list[str], meals: dict) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    weekday = today.strftime("%A")
    date_str = today.strftime("%B %d, %Y")

    tasks_text = "\n".join(f"• {t}" for t in tasks) if tasks else "No scheduled tasks today."
    meals_text = (
        f"Breakfast: {meals.get('breakfast', 'Not planned')}\n"
        f"Lunch: {meals.get('lunch', 'Not planned')}\n"
        f"Dinner: {meals.get('dinner', 'Not planned')}\n"
        f"Snacks: {', '.join(meals.get('snacks', ['Not planned']))}"
        if meals
        else "No meals planned for today."
    )

    prompt = f"""You are a warm, enthusiastic personal butler. Your job is to send a morning WhatsApp message to {name}.

Today is {weekday}, {date_str}.

Their tasks for today:
{tasks_text}

Their meal plan for today:
{meals_text}

Write a short, friendly morning WhatsApp message (max 250 words) that:
1. Opens with a warm, uplifting greeting using their name and today's day
2. Briefly summarises their key tasks for the day in a motivating way
3. Mentions today's meal plan in an appetising way
4. Closes with a short energising sign-off

Keep it conversational, like a message from a caring friend, not a formal report.
Use emojis sparingly but effectively. Do NOT use markdown formatting like ** or ## —
this is plain WhatsApp text."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract the text block (thinking blocks come first)
    for block in response.content:
        if block.type == "text":
            return block.text

    return "Good morning! Have a wonderful day ahead."


# ---------------------------------------------------------------------------
# WhatsApp — send via Twilio
# ---------------------------------------------------------------------------

def send_whatsapp(message: str) -> str:
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ["TWILIO_WHATSAPP_FROM"]
    to_number = os.environ["WHATSAPP_TO"]

    twilio = TwilioClient(account_sid, auth_token)
    msg = twilio.messages.create(
        body=message,
        from_=from_number,
        to=to_number,
    )
    return msg.sid


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_butler() -> None:
    name = os.getenv("YOUR_NAME", "friend")
    today = date.today()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Butler running for {today} ({today.strftime('%A')})...")

    tasks_data = load_json("tasks.json")
    meals_data = load_json("meals.json")

    tasks = get_todays_tasks(tasks_data, today)
    meals = get_todays_meals(meals_data, today)

    print(f"  Tasks: {len(tasks)} found")
    print(f"  Meals: {'found' if meals else 'not found'}")

    briefing = generate_briefing(name, today, tasks, meals)
    print(f"\n--- Generated Message ---\n{briefing}\n--- End ---\n")

    sid = send_whatsapp(briefing)
    print(f"  WhatsApp message sent! SID: {sid}")


if __name__ == "__main__":
    run_butler()
