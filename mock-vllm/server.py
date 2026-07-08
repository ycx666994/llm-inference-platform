import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from time import time


class MockVllmHandler(BaseHTTPRequestHandler):
    server_version = "mock-vllm/0.1"

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        if self.path == "/v1/models":
            self._send_json(
                200,
                {
                    "object": "list",
                    "data": [
                        {
                            "id": "Qwen/Qwen2.5-0.5B-Instruct",
                            "object": "model",
                            "created": int(time()),
                            "owned_by": "mock",
                        }
                    ],
                },
            )
            return

        self._send_json(404, {"detail": "Not found"})

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self._send_json(404, {"detail": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self._send_json(400, {"detail": "Invalid JSON"})
            return

        model = payload.get("model", "Qwen/Qwen2.5-0.5B-Instruct")
        user_message = self._last_user_message(payload)
        answer = f"Mock response from {model}. Received: {user_message}"

        self._send_json(
            200,
            {
                "id": "chatcmpl-mock",
                "object": "chat.completion",
                "created": int(time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": answer,
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 16,
                    "completion_tokens": 16,
                    "total_tokens": 32,
                },
            },
        )

    def log_message(self, format: str, *args) -> None:
        print(f"{self.address_string()} - {format % args}")

    def _send_json(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def _last_user_message(payload: dict) -> str:
        messages = payload.get("messages", [])
        for message in reversed(messages):
            if message.get("role") == "user":
                return str(message.get("content", ""))
        return ""


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8000), MockVllmHandler)
    print("Mock vLLM server listening on http://0.0.0.0:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()

