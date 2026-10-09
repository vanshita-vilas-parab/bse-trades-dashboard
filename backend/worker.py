import os
import requests
from status import set_status
from events import notify_clients
from dotenv import load_dotenv

load_dotenv()

BSE_API_URL = os.getenv(
    "BSE_API_URL",
    "http://127.0.0.1:5001/getTrades"
)

def pull_trades_from_bse():
    print("Background pull started.")

    try:
        response = requests.get(
            BSE_API_URL,
            timeout=1000
        )

        response.raise_for_status()

        data = response.json()

        print(f"Received {data['count']} trades from Mock BSE.")

        save_trades(data["trades"])

        print("Trades saved successfully.")

        set_status("completed")

        notify_clients("pull_completed")

    except requests.RequestException as error:
        print(f"BSE API request failed: {error}")

        set_status("failed")

        notify_clients("pull_failed")


def save_trades(trades):
    from database import get_connection

    connection = get_connection()

    for trade in trades:
        connection.execute("""
            INSERT OR IGNORE INTO trades
            (trade_id, client, symbol, quantity, price, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            trade["tradeId"],
            trade["client"],
            trade["symbol"],
            trade["quantity"],
            trade["price"],
            trade["timestamp"]
        ))

    connection.commit()
    connection.close()