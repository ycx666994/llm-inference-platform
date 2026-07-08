import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    steady_load: {
      executor: "constant-vus",
      vus: Number(__ENV.VUS || 5),
      duration: __ENV.DURATION || "1m",
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<30000"],
  },
};

const baseUrl = __ENV.BASE_URL || "http://localhost:8080";
const apiKey = __ENV.API_KEY || "sk-demo";
const model = __ENV.MODEL || "facebook/opt-125m";

export default function () {
  const payload = JSON.stringify({
    model,
    messages: [
      {
        role: "user",
        content: "Give one short sentence about cloud native inference.",
      },
    ],
    max_tokens: 64,
    temperature: 0.2,
  });

  const res = http.post(`${baseUrl}/v1/chat/completions`, payload, {
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
  });

  check(res, {
    "status is 200": (r) => r.status === 200,
  });

  sleep(1);
}
