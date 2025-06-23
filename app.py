import os, time
import requests
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
import pytz

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Amsterdam")

pairs_config = {
    "EURUSD": "OANDA",
    "GBPUSD": "OANDA",
    "USDJPY": "OANDA",
    "USDCHF": "OANDA",
    "AUDUSD": "OANDA",
    "USDCAD": "OANDA",
    "NZDUSD": "OANDA"
    # 🔥 XAUUSD is excluded for now
}

def get_handler(symbol, exchange):
    return TA_Handler(
        symbol=symbol,
        exchange=exchange,
        screener="forex",
        interval=Interval.INTERVAL_15_MINUTES
    )

def analyze_and_signal(symbol, exchange):
    try:
        print(f"📊 Analyzing {symbol} on {exchange}")
        handler = get_handler(symbol, exchange)
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
                f"📢 {symbol} {action} SIGNAL\n\n"
                f"🟢 Entry: {entry}\n"
                f"🛡️ SL: {sl}\n"
                f"🎯 TP: {tp}\n"
                f"⏰ 15m TF\n"
                f"🕒 {datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M')}\n"
                f"🚀 Auto from Rockstar Bot"
            )
            response = requests.post(WEBHOOK_URL, json={"text": message})
            if response.status_code == 200:
                print(f"✅ Signal sent for {symbol}")
            else:
                print(f"⚠️ Failed to send signal for {symbol}: {response.status_code} - {response.text}")
        else:
            print(f"ℹ️ No valid signal for {symbol}")

    except Exception as e:
        print(f"❌ Error analyzing {symbol}: {e}")

def run_all():
    for symbol, exchange in pairs_config.items():
        analyze_and_signal(symbol, exchange)
        time.sleep(15)  # Slight delay to prevent 429 rate-limiting

if __name__ == "__main__":
    while True:
        run_all()
        time.sleep(300)