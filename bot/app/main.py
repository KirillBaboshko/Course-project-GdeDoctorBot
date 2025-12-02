"""Telegram bot entry point."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.services.standalone_service import StandaloneDataService
from app.services.ai_assistant import AIAssistant
from app.handlers import start, standalone_search, standalone_review, ai_search
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
    
    # Initialize AI assistant if credentials provided
    if config.GIGACHAT_CREDENTIALS:
        try:
            bot._ai_assistant = AIAssistant(credentials=config.GIGACHAT_CREDENTIALS)
            await bot._ai_assistant.initialize()
            logger.info("AI Assistant: Enabled")
        except Exception as e:
            logger.warning(f"Failed to initialize AI Assistant: {e}")
            logger.info("AI Assistant: Disabled")
            bot._ai_assistant = None
    else:
        bot._ai_assistant = None
        logger.info("AI Assistant: Disabled (no credentials)")

    # Register routers
    dp.include_router(start.router)
    dp.include_router(standalone_search.router)
    dp.include_router(standalone_review.router)
    
    # Register AI search router if AI is enabled
    if bot._ai_assistant:
        dp.include_router(ai_search.router)

    logger.info("Starting bot...")
    logger.info(f"Database: {config.DATABASE_PATH}")
    logger.info(f"Yandex API: {'Enabled' if config.YANDEX_API_KEY else 'Disabled'}")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Close services
        if hasattr(bot, '_data_service'):
            await bot._data_service.close()
        if hasattr(bot, '_ai_assistant') and bot._ai_assistant:
            await bot._ai_assistant.close()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
