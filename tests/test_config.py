from __future__ import annotations

import json

import pytest

from app.config import load_prize_config


def _write_config(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _base_payload():
    return {
        "not_winner_message": "很抱歉，您没有中奖。",
        "already_claimed_message": "您已经领取过奖品，请勿重复领取。",
        "winner_message_template": "恭喜您中奖！\n\n您的奖品是：\n{prize}",
        "winners": {"123": "示例奖品"},
    }


def test_load_prize_config_success(tmp_path):
    p = tmp_path / "config.json"
    _write_config(p, _base_payload())
    cfg = load_prize_config(p)
    assert cfg.winners[123] == "示例奖品"


def test_missing_required_field_raises(tmp_path):
    payload = _base_payload()
    del payload["winners"]
    p = tmp_path / "config.json"
    _write_config(p, payload)
    with pytest.raises(ValueError, match="Missing required config field"):
        load_prize_config(p)


def test_missing_prize_placeholder_raises(tmp_path):
    payload = _base_payload()
    payload["winner_message_template"] = "恭喜中奖"
    p = tmp_path / "config.json"
    _write_config(p, payload)
    with pytest.raises(ValueError, match="containing '\\{prize\\}'"):
        load_prize_config(p)


def test_winners_not_dict_raises(tmp_path):
    payload = _base_payload()
    payload["winners"] = []
    p = tmp_path / "config.json"
    _write_config(p, payload)
    with pytest.raises(ValueError, match="winners must be an object/dict"):
        load_prize_config(p)


def test_winner_key_not_number_raises(tmp_path):
    payload = _base_payload()
    payload["winners"] = {"abc": "prize"}
    p = tmp_path / "config.json"
    _write_config(p, payload)
    with pytest.raises(ValueError, match="Winner key"):
        load_prize_config(p)


def test_winner_value_empty_raises(tmp_path):
    payload = _base_payload()
    payload["winners"] = {"123": "   "}
    p = tmp_path / "config.json"
    _write_config(p, payload)
    with pytest.raises(ValueError, match="non-empty string"):
        load_prize_config(p)
