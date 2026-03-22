import { useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

export default function StatsPanel() {
  const [shortCode, setShortCode] = useState("");
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setStats(null);
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/stats/${shortCode}`);
      setStats(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Short code not found.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section id="stats">
      <div className="card">
        <h2>URL Stats</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Enter short code"
            value={shortCode}
            onChange={(e) => setShortCode(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Fetching..." : "Get Stats"}
          </button>
        </form>

        {stats && (
          <div className="result">
            <div className="stat-row">
              <span className="stat-label">Original URL</span>
              <span className="stat-value">{stats.original_url}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Click Count</span>
              <span className="stat-value">{stats.click_count}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Created At</span>
              <span className="stat-value">
                {new Date(stats.created_at).toLocaleString()}
              </span>
            </div>
            {stats.expires_at && (
              <div className="stat-row">
                <span className="stat-label">Expires At</span>
                <span className="stat-value">
                  {new Date(stats.expires_at).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        )}

        {error && <p className="error">{error}</p>}
      </div>
    </section>
  );
}
