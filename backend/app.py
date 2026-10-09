from flask import Flask, jsonify, Response
from flask_cors import CORS
from database import initialize_database, get_connection
from worker import pull_trades_from_bse
from events import add_client, remove_client
from status import get_status, set_status
from threading import Thread
import queue

app = Flask(__name__)
CORS(app)

# Create the database/table when the application starts
initialize_database()


@app.route("/api/trades", methods=["GET"])
def get_trades():
    connection = get_connection()

    trades = connection.execute("""
        SELECT trade_id, client, symbol, quantity, price, timestamp
        FROM trades
        ORDER BY timestamp DESC
    """).fetchall()

    connection.close()

    return jsonify({
        "count": len(trades),
        "trades": [dict(trade) for trade in trades]
    })

@app.route("/api/pull", methods=["POST"])
def start_pull():

    if get_status() == "pulling":
        return jsonify({
            "status": "pulling",
            "message": "A trade pull is already in progress."
        }), 409

    set_status("pulling")

    thread = Thread(target=pull_trades_from_bse)
    thread.start()

    return jsonify({
        "status": "pulling",
        "message": "Trade pull started in background."
    })

@app.route("/api/events")
def events():
    client_queue = add_client()

    def event_stream():
        try:
            while True:
                event = client_queue.get()

                yield f"data: {event}\n\n"

        except GeneratorExit:
            remove_client(client_queue)

    return Response(
        event_stream(),
        mimetype="text/event-stream"
    )

@app.route("/api/status", methods=["GET"])
def get_pull_status():
    return jsonify({
        "status": get_status()
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)