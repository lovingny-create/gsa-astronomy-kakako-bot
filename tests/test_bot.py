import unittest
from pathlib import Path

from src.hwbot.bot import BotData, ObservationBot, read_json


ROOT = Path(__file__).resolve().parents[1]


class BotTests(unittest.TestCase):
    def make_bot(self, csv_path: str | None = None) -> ObservationBot:
        config = read_json(ROOT / "data" / "config.example.json")
        if csv_path is not None:
            config["recording"]["csv_path"] = csv_path
        return ObservationBot(
            BotData(
                config=config,
                troubleshooting=read_json(ROOT / "data" / "troubleshooting.json"),
                targets=read_json(ROOT / "data" / "observing_targets.json"),
            )
        )

    def request(self, utterance: str) -> dict:
        return {
            "userRequest": {
                "utterance": utterance,
                "user": {
                    "id": "test-user",
                },
            }
        }

    def text_from(self, response: dict) -> str:
        return response["template"]["outputs"][0]["simpleText"]["text"]

    def test_focus_question_returns_focus_steps(self):
        bot = self.make_bot()
        response = bot.handle_skill(self.request("초점이 안 맞아요"))
        self.assertIn("초점", self.text_from(response))

    def test_solar_question_returns_safety_first(self):
        bot = self.make_bot()
        response = bot.handle_skill(self.request("태양을 망원경으로 봐도 돼?"))
        self.assertIn("절대", self.text_from(response))

    def test_record_writes_csv(self):
        csv_path = ROOT / ".test_tmp" / "records.csv"
        if csv_path.exists():
            csv_path.unlink()
        bot = self.make_bot(".test_tmp/records.csv")
        response = bot.handle_skill(self.request("기록: 대상=달, 메모=잘 보임"))
        self.assertIn("저장했습니다", self.text_from(response))
        self.assertTrue(csv_path.exists())


if __name__ == "__main__":
    unittest.main()
