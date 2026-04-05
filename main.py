import os
import requests
import stripe

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (needed for frontend → backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stripe setup
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# -----------------------
# Health check
# -----------------------
@app.get("/health")
def health():
    return {"ok": True, "env": "production"}


# -----------------------
# Analysis endpoint
# -----------------------
@app.post("/api/analyze")
def analyze(data: dict):
    query = data.get("query", "Unknown Card")

    return {
        "ok": True,
        "result": {
            "card": {
                "name": query,
                "raw_low": 70,
                "raw_high": 100,
                "psa10_low": 300,
                "psa10_high": 400,
                "trend_30d_pct": 8,
                "gem_rate_pct": 55,
                "set_name": "Prizm",
                "sport": "Basketball",
                "era": "Modern"
            },
            "spread_multiple": 3.8,
            "expected_roi_pct": 42.5,
            "estimated_expected_profit": 85,
            "estimated_profit_if_gem": 220,
            "grade_signal": "STRONG GRADE",
            "flip_signal": "BUY",
            "confidence": "High",
            "risk_band": "Medium",
            "reasons_to_buy": ["Strong spread", "High demand"],
            "reasons_to_pass": ["Condition sensitive"]
        }
    }


# -----------------------
# Website → Telegram handoff
# -----------------------
@app.post("/api/site/lead")
def lead():
    return {
        "ok": True,
        "telegram_url": "https://t.me/CARDHARDBOT"
    }


# -----------------------
# Telegram webhook
# -----------------------
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


# -----------------------
# Stripe checkout
# -----------------------
@app.post("/api/create-checkout-session")
def create_checkout_session():
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": os.getenv("STRIPE_PRICE_ID"), "quantity": 1}],
        success_url=f"{os.getenv('PUBLIC_BASE_URL')}/success",
        cancel_url=f"{os.getenv('PUBLIC_BASE_URL')}/cancel",
    )
    return {"ok": True, "url": session.url}


# -----------------------
# Stripe webhook
# -----------------------
@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(alias="Stripe-Signature")):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            os.getenv("STRIPE_WEBHOOK_SECRET"),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("Payment complete:", session.get("id"))

    return {"ok": True}
