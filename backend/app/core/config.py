import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Settings:
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    CAL_API_KEY: Optional[str] = os.getenv("CAL_API_KEY")
    CAL_API_VERSION: str = os.getenv("CAL_API_VERSION", "2026-02-25")
    CAL_USERNAME: Optional[str] = os.getenv("CAL_USERNAME")
    CAL_EVENT_TYPE_SLUG: Optional[str] = os.getenv("CAL_EVENT_TYPE_SLUG")
    CAL_TIMEZONE: str = os.getenv("CAL_TIMEZONE", "America/Los_Angeles")


settings = Settings()