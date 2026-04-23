from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .bot import ObservationBot


class SkillRequestHandler(BaseHTTPRequestHandler):
    bot: ObservationBot

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self.write_json({"ok": True})
            return
        self.write_json(
            {
                "service": "school-astronomy-kakao-chatbot",
                "endpoints": ["/health", "/skill"],
            }
        )

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/skill":
            self.write_json({"error": "not found"}, status=404)
            return

        try:
            payload = self.read_json()
            response = self.bot.handle_skill(payload)
            self.write_json(response)
        except Exception as exc:  # Kakao should receive a friendly response.
            self.write_json(
                {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            {
                                "simpleText": {
                                    "text": f"서버 오류가 발생했습니다. 담당자에게 알려 주세요: {exc}"
                                }
                            }
                        ]
                    },
                },
                status=200,
            )

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def write_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


def main() -> None:
    config_path_value = os.environ.get("HWBOT_CONFIG")
    config_path = Path(config_path_value) if config_path_value else None
    bot = ObservationBot.from_files(config_path)
    SkillRequestHandler.bot = bot

    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), SkillRequestHandler)
    print(f"Listening on http://localhost:{port}")
    print("Kakao skill endpoint: POST /skill")
    server.serve_forever()

