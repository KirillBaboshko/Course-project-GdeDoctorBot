"""Telegram bot entry point."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.services.standalone_service import StandaloneDataService
from app.handlers import start, standalone_search, standalone_review
from app.standalone_config import StandaloneBotConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


async def main():
    """Main bot function."""
    # Initialize config
    config = StandaloneBotConfig()
    
    # Initialize bot and dispatcher
    bot = Bot(token=config.TELEGRAM_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Initialize data service and attach to bot
    bot._data_service = StandaloneDataService(
        db_path=config.DATABASE_PATH, 
        yandex_api_key=config.YANDEX_API_KEY
    )

    # Register routers
    dp.include_router(start.router)
    dp.include_router(standalone_search.router)
    dp.include_router(standalone_review.router)

    logger.info("Starting bot...")
    logger.info(f"Database: {config.DATABASE_PATH}")
    logger.info(f"Yandex API: {'Enabled' if config.YANDEX_API_KEY else 'Disabled'}")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Close data service
        if hasattr(bot, '_data_service'):
            await bot._data_service.close()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
