from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    bot_token: str
    config_path: Path
    database_path: Path


@dataclass(frozen=True)
class PrizeConfig:
    not_winner_message: str
    already_claimed_message: str
    winner_message_template: str
    winners: dict[int, str]


def load_app_config() -> AppConfig:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise ValueError("Missing BOT_TOKEN in .env")

    config_path = Path(os.getenv("CONFIG_PATH", "config.json")).expanduser()
    database_path = Path(os.getenv("DATABASE_PATH", "data/claims.db")).expanduser()

    return AppConfig(
        bot_token=bot_token,
        config_path=config_path,
        database_path=database_path,
    )


def load_prize_config(config_path: Path) -> PrizeConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc

    required_fields = [
        "not_winner_message",
        "already_claimed_message",
        "winner_message_template",
        "winners",
    ]
    for field in required_fields:
        if field not in raw:
            raise ValueError(f"Missing required config field: {field}")

    winner_template = raw["winner_message_template"]
    if not isinstance(winner_template, str) or "{prize}" not in winner_template:
        raise ValueError("winner_message_template must be a string containing '{prize}'")

    winners_raw = raw["winners"]
    if not isinstance(winners_raw, dict):
        raise ValueError("winners must be an object/dict")

    winners: dict[int, str] = {}
    for k, v in winners_raw.items():
        try:
            tg_id = int(k)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Winner key must be integer-like Telegram ID string: {k}") from exc

        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"Winner prize for tg_id={k} must be a non-empty string")

        winners[tg_id] = v

    for field in ["not_winner_message", "already_claimed_message"]:
        if not isinstance(raw[field], str) or not raw[field].strip():
            raise ValueError(f"{field} must be a non-empty string")

    return PrizeConfig(
        not_winner_message=raw["not_winner_message"],
        already_claimed_message=raw["already_claimed_message"],
        winner_message_template=winner_template,
        winners=winners,
    )
