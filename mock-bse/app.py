from flask import Flask, jsonify
import time
import os
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DELAY_SECONDS = int(os.getenv("BSE_DELAY_SECONDS", 10))

SYMBOLS = [
    "TCS",
    "INFY",
    "RELIANCE",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "WIPRO",
    "ITC",
    "LT",
    "BHARTIARTL"
]

BATCH_SIZE = 5000

next_trade_id = 1


@app.route("/getTrades", methods=["GET"])
def get_trades():
    global next_trade_id

    print(f"Mock BSE: waiting {DELAY_SECONDS} seconds...")

    time.sleep(DELAY_SECONDS)

    trades = []

    start_id = next_trade_id
    end_id = start_id + BATCH_SIZE

    start_time = datetime.now()

    for trade_number in range(start_id, end_id):
        trade = {
            "tradeId": f"TRD{trade_number:05d}",
            "client": f"CLIENT{random.randint(1, 500):03d}",
            "symbol": random.choice(SYMBOLS),
            "quantity": random.randint(10, 1000),
            "price": round(random.uniform(500, 4000), 2),
            "timestamp": (
                start_time + timedelta(
                    seconds=random.randint(0, 21600)
                )
            ).isoformat()
        }

        trades.append(trade)

    next_trade_id = end_id

    return jsonify({
        "count": len(trades),
        "trades": trades
    })


if __name__ == "__main__":
    app.run(port=5001, debug=True)