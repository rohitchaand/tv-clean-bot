import os, time
import requests
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
import pytz
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Amsterdam")

pairs_config = {
pairs_config = {
    "EURUSD": "OANDA",
    "GBPUSD": "OANDA",
    "USDJPY": "OANDA",
    "USDCHF": "OANDA",
    "AUDUSD": "OANDA",
    "USDCAD": "OANDA",
    "NZDUSD": "OANDA",
    "XAUUSD": "FOREXCOM"  # ← Fixed exchange for gold
}

def get_handler(pair, exchange):
    symbol = "XAUUSD" if pair == "XAUUSD" else pair
    return TA_Handler(
        symbol=symbol,
        exchange=exchange,
        screener="forex",
        interval=Interval.INTERVAL_15_MINUTES
    )

def analyze_and_signal(pair_label, symbol, exchange):
    try:
        print(f"📊 Analyzing {pair_label} on {exchange}")
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
                f"📢 {pair_label} {action} SIGNAL\n\n"
                f"🟢 Entry: {entry}\n"
                f"🎯 TP: {tp}\n"
                f"🛡️ SL: {sl}\n"
                f"⏰ 15m TF\n"
                f"🕒 {datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M')}\n"
                f"🚀 Auto from Rockstar Bot"
            )
            response = requests.post(WEBHOOK_URL, json={"text": message})
            print(f"✅ Signal sent for {pair_label}" if response.status_code == 200 else f"⚠️ Failed: {response.text}")
        else:
            print(f"ℹ️ No valid signal for {pair_label}")
    except Exception as e:
        print(f"❌ Error analyzing {pair_label}: {e}")

import random

def run_all():
    pairs = list(pairs_config.items())
    random.shuffle(pairs)  # Randomize order

    for pair_label, exchange in pairs:
        analyze_and_signal(pair_label, exchange)
        time.sleep(random.randint(25, 40))  # Delay between 25–40 seconds

def run_test():
    analyze_and_signal("XAUUSD", "XAUUSD", "OANDA")
    print("✅ Test complete.")

if __name__ == "__main__":
    if os.getenv("SEND_TEST", "false").lower() == "true":
        run_test()
    else:
        while True:
            run_all()
            time.sleep(300)
