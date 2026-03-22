import { useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

export default function ShortenForm() {
  const [url, setUrl] = useState("");
  const [expiresInHours, setExpiresInHours] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const normalizedUrl =
        url.startsWith("http://") || url.startsWith("https://")
          ? url
          : `https://${url}`;
      const payload = { url: normalizedUrl };
      if (expiresInHours !== "") {
        payload.expires_in_hours = parseInt(expiresInHours, 10);
      }
      const res = await axios.post(`${API_BASE}/shorten`, payload);
      const data = res.data;
      data.short_url = `${window.location.origin}/${data.short_code}`;
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section id="shorten">
      <div className="card">
        <h2>Shorten a URL</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="https://your-long-url.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
          <input
            type="number"
            placeholder="Expires in hours (optional)"
            value={expiresInHours}
            onChange={(e) => setExpiresInHours(e.target.value)}
            min="1"
          />
          <button type="submit" disabled={loading}>
            {loading ? "Shortening..." : "Shorten"}
          </button>
        </form>

        {result && (
          <div className="result">
            <div className="stat-row">
              <span className="stat-label">Short URL</span>
              <a href={result.short_url} target="_blank" rel="noreferrer">
                {result.short_url}
              </a>
            </div>
            <div className="stat-row">
              <span className="stat-label">Short Code</span>
              <span className="stat-value">{result.short_code}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Created At</span>
              <span className="stat-value">
                {new Date(result.created_at).toLocaleString()}
              </span>
            </div>
            {result.expires_at && (
              <div className="stat-row">
                <span className="stat-label">Expires At</span>
                <span className="stat-value">
                  {new Date(result.expires_at).toLocaleString()}
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
