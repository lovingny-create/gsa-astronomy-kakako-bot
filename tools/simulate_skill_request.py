from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.hwbot.bot import ObservationBot


def main() -> None:
    utterance = " ".join(sys.argv[1:]) or "메뉴"
    config_path_value = os.environ.get("HWBOT_CONFIG")
    config_path = Path(config_path_value) if config_path_value else None
    bot = ObservationBot.from_files(config_path)
    payload = {
        "userRequest": {
            "utterance": utterance,
            "user": {
                "id": "local-test-user",
            },
        }
    }
    print(json.dumps(bot.handle_skill(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
