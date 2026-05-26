from __future__ import annotations

from dataclasses import dataclass

from app.config import PrizeConfig
from app.database import ClaimsRepository


@dataclass(frozen=True)
class ClaimResult:
    message: str
    is_winner: bool
    already_claimed: bool
    claimed_now: bool


def build_claim_response(tg_id: int, prize_config: PrizeConfig, repo: ClaimsRepository) -> ClaimResult:
    prize = prize_config.winners.get(tg_id)
    if prize is None:
        return ClaimResult(
            message=prize_config.not_winner_message,
            is_winner=False,
            already_claimed=False,
            claimed_now=False,
        )

    if repo.has_claimed(tg_id):
        return ClaimResult(
            message=prize_config.already_claimed_message,
            is_winner=True,
            already_claimed=True,
            claimed_now=False,
        )

    if not repo.try_claim(tg_id, prize):
        return ClaimResult(
            message=prize_config.already_claimed_message,
            is_winner=True,
            already_claimed=True,
            claimed_now=False,
        )

    return ClaimResult(
        message=prize_config.winner_message_template.format(prize=prize),
        is_winner=True,
        already_claimed=False,
        claimed_now=True,
    )
