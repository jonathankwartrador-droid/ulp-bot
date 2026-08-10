#!/usr/bin/env python3
"""
ULP Telegram Bot - Main Entry Point
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.bot import ULPBot


def main():
    """Main function"""
    bot = ULPBot("config.json")
    bot.setup_logging("logs/")

    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
