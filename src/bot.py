import logging
import json
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

from .database import Database
from .parser import ULPParser
from .inventory import InventoryManager
from .search import SearchEngine
from .generator import CredentialGenerator
from .user_manager import UserManager
from .export import ExportManager
from .handlers.user_handlers import UserHandlers
from .handlers.admin_handlers import AdminHandlers
from .handlers.inline_handlers import InlineHandlers

logger = logging.getLogger(__name__)


class ULPBot:
    """Main ULP Telegram Bot"""

    def __init__(self, config_path: str = "config.json"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Initialize components
        self.db = Database(self.config['database_path'])
        self.inventory = InventoryManager(self.config['inventory_path'], self.db)
        self.search_engine = SearchEngine(self.inventory, self.db)
        self.export_manager = ExportManager(self.config.get('export_path', 'exports/'))

        self.user_manager = UserManager(self.db, self.config)

        # Initialize handlers
        self.user_handlers = UserHandlers(self)
        self.admin_handlers = AdminHandlers(self)
        self.inline_handlers = InlineHandlers(self)

        # Application
        self.app = None

        logger.info("ULP Bot initialized")

    async def initialize_app(self):
        """Initialize Telegram application"""
        self.app = Application.builder().token(self.config['bot_token']).build()

        # Register command handlers
        self.app.add_handler(CommandHandler("start", self.user_handlers.start))
        self.app.add_handler(CommandHandler("help", self.user_handlers.help_command))
        self.app.add_handler(CommandHandler("profile", self.user_handlers.profile))
        self.app.add_handler(CommandHandler("balance", self.user_handlers.balance))
        self.app.add_handler(CommandHandler("stats", self.user_handlers.stats))
        self.app.add_handler(CommandHandler("inventory", self.user_handlers.inventory))
        self.app.add_handler(CommandHandler("history", self.user_handlers.history))
        self.app.add_handler(CommandHandler("settings", self.user_handlers.settings))

        # Admin commands
        self.app.add_handler(CommandHandler("admin", self.admin_handlers.admin_panel))
        self.app.add_handler(CommandHandler("users", self.admin_handlers.manage_users))
        self.app.add_handler(CommandHandler("addcredits", self.admin_handlers.add_credits))
        self.app.add_handler(CommandHandler("removecredits", self.admin_handlers.remove_credits))
        self.app.add_handler(CommandHandler("banuser", self.admin_handlers.ban_user))
        self.app.add_handler(CommandHandler("unbanuser", self.admin_handlers.unban_user))
        self.app.add_handler(CommandHandler("reload", self.admin_handlers.reload_inventory))

        # Callback handlers
        self.app.add_handler(CallbackQueryHandler(self.inline_handlers.button_callback))

        # Message handlers for conversation
        search_conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.inline_handlers.start_search, pattern="^search$"),
                CommandHandler("search", self.inline_handlers.start_search)
            ],
            states={
                1: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.inline_handlers.search_domain_input)]
            },
            fallbacks=[]
        )

        gen_conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.inline_handlers.start_generate, pattern="^gen_")
            ],
            states={
                2: [CallbackQueryHandler(self.inline_handlers.select_inventory, pattern="^gen_inv_")],
                3: [CallbackQueryHandler(self.inline_handlers.select_quantity, pattern="^qty_")],
                4: [CallbackQueryHandler(self.inline_handlers.confirm_generation, pattern="^fmt_")]
            },
            fallbacks=[]
        )

        self.app.add_handler(search_conv_handler)
        self.app.add_handler(gen_conv_handler)

        logger.info("Telegram application initialized")

    async def run(self):
        """Run the bot (blocking)"""
        try:
            await self.initialize_app()
            async with self.app:
                await self.app.initialize()
                await self.app.start()
                await self.app.updater.start_polling()

                logger.info("Bot is running. Press Ctrl+C to stop.")
                await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            if self.app:
                await self.app.updater.stop()
                await self.app.stop()
                await self.app.shutdown()

            logger.info("Bot stopped")

    def setup_logging(self, log_path: str = "logs/"):
        """Setup logging"""
        Path(log_path).mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_path}/bot.log'),
                logging.StreamHandler()
            ]
        )

        logger.info("Logging configured")


async def main():
    """Main entry point"""
    bot = ULPBot("config.json")
    bot.setup_logging("logs/")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
