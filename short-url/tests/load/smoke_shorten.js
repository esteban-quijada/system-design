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

export default function () {
  const payload = JSON.stringify({ url: "https://example.com/" });
  const params = { headers: { "Content-Type": "application/json" } };

  const res = http.post(`${BASE_URL}/shorten`, payload, params);

  check(res, {
    "status is 200": (r) => r.status === 200,
    "response has short_code": (r) => JSON.parse(r.body).short_code !== undefined,
    "response has short_url": (r) => JSON.parse(r.body).short_url !== undefined,
    "response has created_at": (r) => JSON.parse(r.body).created_at !== undefined,
  });

  sleep(1);
}
