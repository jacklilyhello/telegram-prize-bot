from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import PrizeConfig
from app.database import ClaimsRepository

logger = logging.getLogger(__name__)

PRIVATE_CHAT_REMINDER = "请私聊机器人领取奖品。"


def build_router(prize_config: PrizeConfig, repo: ClaimsRepository) -> Router:
    router = Router()

    @router.message(CommandStart(), ~F.chat.type.in_({"private"}))
    async def start_non_private(message: Message) -> None:
        await message.reply(PRIVATE_CHAT_REMINDER)

    @router.message(CommandStart(), F.chat.type == "private")
    async def start_private(message: Message) -> None:
        if message.from_user is None:
            return

        tg_id = message.from_user.id
        logger.info("User %s sent /start", tg_id)

        prize = prize_config.winners.get(tg_id)
        if prize is None:
            logger.info("User %s is not winner", tg_id)
            await message.reply(prize_config.not_winner_message)
            return

        logger.info("User %s is winner", tg_id)

        if repo.has_claimed(tg_id):
            logger.info("User %s already claimed", tg_id)
            await message.reply(prize_config.already_claimed_message)
            return

        claimed = repo.try_claim(tg_id, prize)
        if not claimed:
            logger.info("User %s already claimed", tg_id)
            await message.reply(prize_config.already_claimed_message)
            return

        logger.info("User %s claimed prize", tg_id)
        await message.reply(prize_config.winner_message_template.format(prize=prize))

    return router
