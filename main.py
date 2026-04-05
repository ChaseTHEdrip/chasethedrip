import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        requests.post(
            f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": f"Chase the Drip is live.\n\nYou said: {text}"
            }
        )

    return {"ok": True}
