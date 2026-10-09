import json
import random
from datetime import datetime, timedelta

random.seed(42)

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

trades = []

start_time = datetime(2026, 10, 9, 9, 15, 0)

for i in range(1, 5001):
    trade = {
        "tradeId": f"TRD{i:05d}",
        "client": f"CLIENT{random.randint(1, 500):03d}",
        "symbol": random.choice(SYMBOLS),
        "quantity": random.randint(10, 1000),
        "price": round(random.uniform(500, 4000), 2),
        "timestamp": (
            start_time + timedelta(seconds=random.randint(0, 21600))
        ).isoformat()
    }

    trades.append(trade)

with open("trades.json", "w") as file:
    json.dump(trades, file, indent=2)

print(f"Generated {len(trades)} trades.")