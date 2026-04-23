from __future__ import annotations

from typing import Any


DEFAULT_QUICK_REPLIES = [
    ("오늘 관측 가능?", "오늘 관측 가능?"),
    ("장비 문제", "장비가 이상해요"),
    ("대상 추천", "뭘 보면 좋을까요?"),
    ("기록", "관측 기록하기"),
    ("안전", "안전/비상 안내"),
]


def quick_reply(label: str, message_text: str) -> dict[str, str]:
    return {
        "label": label,
        "action": "message",
        "messageText": message_text,
    }


def simple_text_response(
    text: str,
    quick_replies: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    replies = quick_replies if quick_replies is not None else DEFAULT_QUICK_REPLIES
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": text[:990],
                    }
                }
            ],
            "quickReplies": [quick_reply(label, message) for label, message in replies],
        },
    }


def extract_utterance(payload: dict[str, Any]) -> str:
    user_request = payload.get("userRequest") or {}
    utterance = user_request.get("utterance") or ""
    return str(utterance).strip()


def extract_user_id(payload: dict[str, Any]) -> str:
    user_request = payload.get("userRequest") or {}
    user = user_request.get("user") or {}
    user_id = user.get("id") or user.get("properties", {}).get("botUserKey")
    return str(user_id or "anonymous")

