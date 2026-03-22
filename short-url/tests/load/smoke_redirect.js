import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 2,
  duration: "30s",
  thresholds: {
    http_req_duration: ["p(95)<500"], // 95% of requests under 500ms
    http_req_failed: ["rate<0.01"],   // error rate under 1%
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

// Shorten a URL once before the test run to get a valid short code
export function setup() {
  const payload = JSON.stringify({ url: "https://example.com/" });
  const params = { headers: { "Content-Type": "application/json" } };
  const res = http.post(`${BASE_URL}/shorten`, payload, params);
  return { short_code: JSON.parse(res.body).short_code };
}

export default function (data) {
  const res = http.get(`${BASE_URL}/${data.short_code}`, {
    redirects: 0, // don't follow the redirect
  });

  check(res, {
    "status is 307": (r) => r.status === 307,
    "location header present": (r) => r.headers["Location"] !== undefined,
  });

  sleep(1);
}
