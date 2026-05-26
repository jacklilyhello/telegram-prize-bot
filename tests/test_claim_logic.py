from __future__ import annotations

from app.claim_service import build_claim_response
from app.config import PrizeConfig
from app.database import ClaimsRepository


def _cfg() -> PrizeConfig:
    return PrizeConfig(
        not_winner_message="很抱歉，您没有中奖。",
        already_claimed_message="您已经领取过奖品，请勿重复领取。",
        winner_message_template="恭喜您中奖！\n\n您的奖品是：\n{prize}",
        winners={1001: "奖品A", 1002: "奖品B"},
    )


def test_non_winner_message(tmp_path):
    repo = ClaimsRepository(tmp_path / "claims.db")
    repo.init()
    res = build_claim_response(5555, _cfg(), repo)
    assert res.message == "很抱歉，您没有中奖。"
    assert res.is_winner is False


def test_winner_first_claim_then_repeat(tmp_path):
    repo = ClaimsRepository(tmp_path / "claims.db")
    repo.init()
    first = build_claim_response(1001, _cfg(), repo)
    second = build_claim_response(1001, _cfg(), repo)

    assert "奖品A" in first.message
    assert first.claimed_now is True
    assert second.message == "您已经领取过奖品，请勿重复领取。"
    assert second.already_claimed is True


def test_one_user_cannot_claim_another_prize(tmp_path):
    repo = ClaimsRepository(tmp_path / "claims.db")
    repo.init()
    _ = build_claim_response(1001, _cfg(), repo)
    repeat = build_claim_response(1001, _cfg(), repo)
    assert "奖品B" not in repeat.message


def test_different_winners_get_their_own_prizes(tmp_path):
    repo = ClaimsRepository(tmp_path / "claims.db")
    repo.init()
    res1 = build_claim_response(1001, _cfg(), repo)
    res2 = build_claim_response(1002, _cfg(), repo)
    assert "奖品A" in res1.message
    assert "奖品B" in res2.message
