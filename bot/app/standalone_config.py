"""Standalone bot configuration - works without backend."""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


@dataclass
class StandaloneBotConfig:
    """Standalone bot configuration."""

    # Telegram
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    
    # Yandex Maps (optional)
    YANDEX_API_KEY: str = os.getenv("YANDEX_API_KEY", "")
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(Path(__file__).parent.parent.parent / "medical_data.db"))
    
    # Pagination
    ITEMS_PER_PAGE: int = 10
    MAX_ITEMS_FETCH: int = 100
    
    # Messages
    SEARCH_HEADER: str = "🔍 <b>Поиск врача</b>\n\n"
    
    # Bot settings
    BOT_NAME: str = "GdeDoctor Bot"
    BOT_DESCRIPTION: str = "Поиск врачей в медицинских учреждениях"

    def __post_init__(self):
        """Validate configuration."""
        if not self.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN is required")
        
        # Yandex API key is optional for basic functionality
        if not self.YANDEX_API_KEY:
            print("⚠️  YANDEX_API_KEY not set. Maps functionality will be disabled.")


config = StandaloneBotConfig()
