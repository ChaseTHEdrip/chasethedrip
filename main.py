from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (important for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "env": "production"}

@app.post("/api/analyze")
def analyze(data: dict):
    return {
        "ok": True,
        "result": {
            "card": {
                "name": data.get("query"),
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

@app.post("/api/site/lead")
def lead():
    return {
        "ok": True,
        "telegram_url": "https://t.me/CARDHARDBOT"
    }
