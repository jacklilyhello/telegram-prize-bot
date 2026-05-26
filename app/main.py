from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import load_app_config, load_prize_config
from app.database import ClaimsRepository
from app.handlers import build_router


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def run() -> None:
    setup_logging()

    app_cfg = load_app_config()
    prize_cfg = load_prize_config(app_cfg.config_path)

    repo = ClaimsRepository(app_cfg.database_path)
    repo.init()

    logger = logging.getLogger(__name__)
    logger.info("Database initialized successfully")

    bot = Bot(token=app_cfg.bot_token)
    dp = Dispatcher()
    dp.include_router(build_router(prize_cfg, repo))

    logger.info("Bot started successfully")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
