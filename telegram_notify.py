# telegram_notify.py
import requests
import os
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def format_signal_message(sig):
    return (
        f"🔥 *REVERSAL SIGNAL* — {sig['symbol']}\n"
        f"Pattern: {sig['pattern']}\n"
        f"Entry: `{sig['entry']}`\n"
        f"SL: `{sig['sl']}`\n"
        f"T1: `{sig['t1']}`  |  T2: `{sig['t2']}`\n"
        f"ATR: `{sig['atr']}` | ADX: `{sig['adx']}`\n"
        f"Vol: `{sig['volume']}` (avg `{sig['vol_sma']}`)\n"
        f"Confidence: *{sig['confidence']}%*\n\n"
        f"_Rules: ADX<{ADX_THRESHOLD}, EMA20/50 reversal, ATR SL {ATR_SL_MULT}x_\n"
    )

def send_signal(sig):
    text = format_signal_message(sig)
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    r = requests.post(API_URL, data=payload)
    try:
        return r.json()
    except:
        return {"ok": False, "status_code": r.status_code, "text": r.text}
