import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [trades, setTrades] = useState([]);
  const [status, setStatus] = useState("Idle");
  const [isPulling, setIsPulling] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrades();

    const eventSource = new EventSource(
      "http://127.0.0.1:5000/api/events"
    );

  eventSource.onmessage = (event) => {
    if (event.data === "pull_completed") {
      setStatus("Completed");
      setIsPulling(false);
      fetchTrades();
    }

    if (event.data === "pull_failed") {
      setStatus("Failed");
      setIsPulling(false);
    }
  };

    eventSource.onerror = (error) => {
      console.error("SSE connection error:", error);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const fetchTrades = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/trades");
      const data = await response.json();

      setTrades(data.trades);
    } catch (error) {
      console.error("Failed to fetch trades:", error);
    } finally {
      setLoading(false);
    }
  };

  const startPull = async () => {
    if (isPulling) {
      return;
    }

    try {
      setIsPulling(true);
      setStatus("Pulling...");

      const response = await fetch(
        "http://127.0.0.1:5000/api/pull",
        {
          method: "POST",
        }
      );

      if (response.status === 409) {
        setStatus("Pull already in progress");
        setIsPulling(true);
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to start pull");
      }

    } catch (error) {
      console.error("Failed to start pull:", error);
      setStatus("Failed");
      setIsPulling(false);
    }
  };

  return (
    <div className="app">
      <h1>BSE Trades Dashboard</h1>

      <div className="controls">
        <p>
          Status: <strong>{status}</strong>
        </p>

        <button
          onClick={startPull}
          disabled={isPulling}
        >
          Pull Latest Trades
        </button>
      </div>

      <div className="summary">
        <h2>Total Trades: {trades.length}</h2>
      </div>

      {loading ? (
        <p>Loading trades...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Trade ID</th>
              <th>Client</th>
              <th>Symbol</th>
              <th>Quantity</th>
              <th>Price</th>
              <th>Timestamp</th>
            </tr>
          </thead>

          <tbody>
            {trades.map((trade) => (
              <tr key={trade.trade_id}>
                <td>{trade.trade_id}</td>
                <td>{trade.client}</td>
                <td>{trade.symbol}</td>
                <td>{trade.quantity}</td>
                <td>{trade.price}</td>
                <td>{trade.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;