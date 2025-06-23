import os
import time
import requests
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
import pytz

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Amsterdam")

# Pairs to analyze — excluding XAUUSD for now
pairs_config = {
    "EURUSD": "OANDA",
    "GBPUSD": "OANDA",
    "USDJPY": "OANDA",
    "USDCHF": "OANDA",
    "AUDUSD": "OANDA",
    "USDCAD": "OANDA",
    "NZDUSD": "OANDA",
}

def get_handler(pair, exchange):
    return TA_Handler(
        symbol=pair,
        exchange=exchange,
        screener="forex",
        interval=Interval.INTERVAL_15_MINUTES
    )

def analyze_and_signal(pair, exchange):
    try:
        print(f"📊 Analyzing {pair} on {exchange}")
        handler = get_handler(pair, exchange)
        analysis = handler.get_analysis()
        summary = analysis.summary
        action = None

        if summary["BUY"] > summary["SELL"] and summary["NEUTRAL"] < summary["BUY"]:
            action = "BUY"
        elif summary["SELL"] > summary["BUY"] and summary["NEUTRAL"] < summary["SELL"]:
            action = "SELL"

        if action:
            entry = round(analysis.indicators["close"], 5)
            sl = round(entry * (0.995 if action == "BUY" else 1.005), 5)
            tp = round(entry * (1.010 if action == "BUY" else 0.990), 5)

            message = (
                f"📢 {pair} {action} SIGNAL\n\n"
                f"🟢 Entry: {entry}\n"
                f"🛡️ SL: {sl}\n"
                f"🎯 TP: {tp}\n"
                f"⏰ 15m TF\n"
                f"🕒 {datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M')}\n"
                f"🚀 Auto from Rockstar Bot"
            )

            response = requests.post(WEBHOOK_URL, json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            })

            if response.status_code == 200:
                print(f"✅ Signal sent for {pair}")
            else:
                print(f"⚠️ Telegram error: {response.status_code} - {response.text}")
        else:
            print(f"ℹ️ No valid signal for {pair}")

    except Exception as e:
        print(f"❌ Error analyzing {pair}: {e}")

def run_all():
    for pair, exchange in pairs_config.items():
        analyze_and_signal(pair, exchange)
        time.sleep(10)

if __name__ == "__main__":
    try:
        print("🚀 Bot started at", datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S'))
        if os.getenv("SEND_TEST") == "true":
            run_test()
        else:
            while True:
                run_all()
                time.sleep(300)
    except Exception as e:
        print("❌ Critical error on startup:", e)