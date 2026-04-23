from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .kakao import extract_user_id, extract_utterance, simple_text_response


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


@dataclass(frozen=True)
class BotData:
    config: dict
    troubleshooting: list[dict]
    targets: list[dict]


class ObservationBot:
    def __init__(self, data: BotData):
        self.data = data

    @classmethod
    def from_files(cls, config_path: Path | None = None) -> "ObservationBot":
        if config_path is None:
            config_path = DATA_DIR / "config.example.json"
        data = BotData(
            config=read_json(config_path),
            troubleshooting=read_json(DATA_DIR / "troubleshooting.json"),
            targets=read_json(DATA_DIR / "observing_targets.json"),
        )
        return cls(data)

    def handle_skill(self, payload: dict) -> dict:
        utterance = extract_utterance(payload)
        user_id = extract_user_id(payload)
        text = normalize(utterance)

        if self.is_emergency(text):
            return self.safety_response()
        if not text or contains_any(text, ["시작", "메뉴", "도움", "help"]):
            return self.welcome_response()
        if contains_any(text, ["기록", "로그", "저장"]):
            return self.record_response(utterance, user_id)
        if contains_any(text, ["관측 가능", "오늘", "날씨", "구름", "습도", "바람"]):
            return self.observing_condition_response()
        if contains_any(text, ["장비", "망원경", "초점", "추적", "정렬", "카메라", "안보", "안 보여", "흐릿", "길게"]):
            return self.troubleshooting_response(text)
        if contains_any(text, ["대상", "추천", "뭘", "무엇", "성운", "성단", "별", "달"]):
            return self.target_response()
        if contains_any(text, ["안전", "비상", "교사", "위험"]):
            return self.safety_response()
        return self.fallback_response()

    def welcome_response(self) -> dict:
        name = self.data.config["school"]["name"]
        return simple_text_response(
            f"{name} 관측 도우미입니다.\n"
            "관측 중 막히면 아래 메뉴를 눌러 주세요.\n\n"
            "처음 버전은 버튼형 진단을 중심으로 답합니다.",
        )

    def observing_condition_response(self) -> dict:
        school = self.data.config["school"]
        weather = self.data.config.get("weather", {})
        live_weather = "꺼짐"
        if weather.get("enable_live_weather"):
            live_weather = "켜짐"

        return simple_text_response(
            f"관측 장소: {school['observing_site']}\n"
            f"위치: {school['latitude']}, {school['longitude']}\n"
            f"실시간 날씨 연동: {live_weather}\n\n"
            "MVP 기준 점검 순서:\n"
            "1. 구름이 많거나 비 예보가 있으면 실내 활동으로 전환\n"
            "2. 습도가 높으면 렌즈 결로 대비\n"
            "3. 바람이 강하면 고배율 관측과 장노출 촬영 피하기\n"
            "4. 달이 밝으면 달/행성/쌍성 위주로 관측",
            [
                ("장비 점검", "장비가 이상해요"),
                ("대상 추천", "뭘 보면 좋을까요?"),
                ("기록", "관측 기록하기"),
                ("안전", "안전/비상 안내"),
            ],
        )

    def troubleshooting_response(self, text: str) -> dict:
        matched = None
        for item in self.data.troubleshooting:
            if any(normalize(keyword) in text for keyword in item["keywords"]):
                matched = item
                break
        if matched is None:
            matched = self.data.troubleshooting[0]

        steps = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(matched["steps"]))
        return simple_text_response(
            f"{matched['title']}\n\n{steps}\n\n"
            "해결되지 않으면 현재 증상을 짧게 다시 보내 주세요.",
            [(reply["label"], reply["message"]) for reply in matched.get("quick_replies", [])]
            or None,
        )

    def target_response(self) -> dict:
        month = now_in_school_tz(self.data.config).month
        season = season_for_month(month)
        candidates = [
            target
            for target in self.data.targets
            if target["season"] in ["all", season]
        ][:5]
        lines = []
        for target in candidates:
            lines.append(
                f"- {target['name']}: {target['difficulty']}, {target['tip']}"
            )
        return simple_text_response(
            f"오늘은 먼저 밝고 찾기 쉬운 대상부터 추천합니다.\n\n"
            + "\n".join(lines)
            + "\n\n행성 위치는 날짜에 따라 크게 달라서, 정식 버전에서는 천문 계산 API로 자동 확인하게 만들 예정입니다.",
            [
                ("오늘 관측 가능?", "오늘 관측 가능?"),
                ("장비 점검", "장비가 이상해요"),
                ("기록", "관측 기록하기"),
                ("메뉴", "메뉴"),
            ],
        )

    def record_response(self, utterance: str, user_id: str) -> dict:
        recording = self.data.config.get("recording", {})
        if recording.get("mode") == "fits_index":
            return self.fits_record_response(utterance, user_id)

        if ":" not in utterance and "：" not in utterance:
            return simple_text_response(
                "관측 기록은 이렇게 보내 주세요.\n\n"
                "기록: 대상=달, 장비=쌍안경, 상태=구름 조금, 메모=크레이터 잘 보임",
                [
                    ("대상 추천", "뭘 보면 좋을까요?"),
                    ("오늘 관측 가능?", "오늘 관측 가능?"),
                    ("메뉴", "메뉴"),
                ],
            )

        saved_path = self.save_record(utterance, user_id)
        return simple_text_response(
            f"관측 기록을 저장했습니다.\n저장 위치: {saved_path}",
            [
                ("추가 기록", "관측 기록하기"),
                ("대상 추천", "뭘 보면 좋을까요?"),
                ("메뉴", "메뉴"),
            ],
        )

    def fits_record_response(self, utterance: str, user_id: str) -> dict:
        if ":" not in utterance and "：" not in utterance:
            return simple_text_response(
                "FITS 관측 기록은 이렇게 보내 주세요.\n\n"
                "기록: fits=20260423_M42_R_001.fits, 대상=M42, 필터=R, 노출=60s, 메모=구름 조금\n\n"
                "카카오톡이 FITS 파일 자체를 안정적으로 보관하는 용도는 아니므로, 봇은 파일명/경로와 관측 조건을 색인으로 저장합니다.",
                [
                    ("장비 문제", "장비가 이상해요"),
                    ("대상 추천", "뭘 보면 좋을까요?"),
                    ("메뉴", "메뉴"),
                ],
            )

        saved_path = self.save_record(utterance, user_id)
        return simple_text_response(
            f"FITS 관측 색인을 저장했습니다.\n저장 위치: {saved_path}\n\n"
            "원본 FITS 파일은 관측 PC나 지정 저장소에 그대로 보관해 주세요.",
            [
                ("추가 기록", "관측 기록하기"),
                ("장비 문제", "장비가 이상해요"),
                ("메뉴", "메뉴"),
            ],
        )

    def safety_response(self) -> dict:
        safety = self.data.config["safety"]
        return simple_text_response(
            "안전 안내입니다.\n\n"
            f"{safety['escalation_message']}\n\n"
            "특히 태양은 전용 태양 필터 없이 절대 망원경/쌍안경으로 보지 마세요.",
            [
                ("교사 호출 기준", "비상 상황 기준"),
                ("장비 문제", "장비가 이상해요"),
                ("메뉴", "메뉴"),
            ],
        )

    def fallback_response(self) -> dict:
        return simple_text_response(
            "아직 그 질문은 정확히 분류하지 못했습니다.\n"
            "아래 메뉴 중 가장 가까운 것을 골라 주세요.\n\n"
            "예: 초점이 안 맞아요 / 별이 길게 찍혀요 / 기록: 대상=달",
        )

    def is_emergency(self, text: str) -> bool:
        keywords = self.data.config["safety"].get("emergency_keywords", [])
        return any(normalize(keyword) in text for keyword in keywords)

    def save_record(self, utterance: str, user_id: str) -> str:
        recording = self.data.config.get("recording", {})
        csv_path = ROOT / recording.get("csv_path", "data/observation_logs.csv")
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        exists = csv_path.exists()
        with csv_path.open("a", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["created_at", "user_id", "raw_text"],
            )
            if not exists:
                writer.writeheader()
            writer.writerow(
                {
                    "created_at": now_in_school_tz(self.data.config).isoformat(),
                    "user_id": user_id,
                    "raw_text": utterance,
                }
            )
        return str(csv_path)


def read_json(path: Path) -> dict | list:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize(text: str) -> str:
    return text.strip().lower().replace(" ", "")


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(normalize(keyword) in text for keyword in keywords)


def now_in_school_tz(config: dict) -> datetime:
    timezone = config.get("school", {}).get("timezone", "Asia/Seoul")
    return datetime.now(ZoneInfo(timezone))


def season_for_month(month: int) -> str:
    if month in [3, 4, 5]:
        return "spring"
    if month in [6, 7, 8]:
        return "summer"
    if month in [9, 10, 11]:
        return "fall"
    return "winter"
