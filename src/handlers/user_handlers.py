import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

# States
SEARCH_DOMAIN, SEARCH_EXACT, SEARCH_INVENTORY = range(3)
GEN_SELECT_DOMAIN, GEN_SELECT_INVENTORY, GEN_SELECT_QUANTITY, GEN_SELECT_FORMAT = range(4)


class UserHandlers:
    """User command handlers"""

    def __init__(self, bot_instance):
        self.bot = bot_instance

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user = self.bot.user_manager.get_or_create_user(
            update.effective_user.id,
            update.effective_user.username
        )

        welcome_text = f"""
🔐 **Welcome to ULP Bot!**

Hello {update.effective_user.first_name}! 👋

This bot helps you search and generate credentials from your ULP inventory.

**Your Stats:**
• Credits: {user['credits']}
• User ID: {user['user_id']}

**What you can do:**
• 🔍 Search for domains in your inventory
• 🏐 Generate credentials in multiple formats
• 📊 View statistics and history
• ⚙️ Manage your settings

Use /help to see all available commands.
        """

        keyboard = [
            [
                InlineKeyboardButton("🔍 Search Domain", callback_data="search"),
                InlineKeyboardButton("📋 Generate", callback_data="generate")
            ],
            [
                InlineKeyboardButton("💰 Balance", callback_data="balance"),
                InlineKeyboardButton("📊 Stats", callback_data="stats")
            ],
            [
                InlineKeyboardButton("📜 History", callback_data="history"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
🆘 **Available Commands:**

**User Commands:**
/start - Start the bot
/help - Show this help message
/profile - View your profile
/balance - Check your credit balance
/search - Search for domains
/inventory - View available inventories
/generate - Generate credentials
/history - View generation history
/stats - View your statistics
/settings - Manage your settings

**Example Usage:**
1. Use /search to find credentials by domain
2. Use /generate to create credentials
3. Export results as TXT

**Output Formats:**
• WITH_URL - domain:login:pass
• WITHOUT_URL - login:pass
• URL_ONLY - domain only
• LOGIN_ONLY - login only

**Need more help?**
Contact admin or use /support
        """

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View user profile"""
        stats = self.bot.user_manager.get_user_stats(update.effective_user.id)

        if not stats:
            await update.message.reply_text("❌ Profile not found")
            return

        profile_text = f"""
👤 **Your Profile**

**User Information:**
• User ID: `{stats['user_id']}`
• Username: @{stats['username']}
• Status: {'🚫 Banned' if stats['is_banned'] else '✅ Active'}
• Admin: {'Yes' if stats['is_admin'] else 'No'}

**Credits & Usage:**
• Balance: {stats['credits']} credits
• Searches Today: {stats['searches_today']}/{stats['searches_limit']}
• Generations Today: {stats['generations_today']}/{stats['generations_limit']}

**Statistics:**
• Total Searches: {stats['total_searches']}
• Total Generations: {stats['total_generations']}
• Member Since: {stats['created_at']}
        """

        await update.message.reply_text(profile_text, parse_mode='Markdown')

    async def balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check credit balance"""
        credits = self.bot.db.get_user_credits(update.effective_user.id)

        balance_text = f"""
💰 **Your Credit Balance**

Current Balance: **{credits}** credits

**Credit Costs:**
• Search: {self.bot.config.get('search_cost', 1)} credit
• Generation: {self.bot.config.get('generation_cost', 2)} credits per item

**How to get more credits:**
Contact admin to purchase credits.
        """

        await update.message.reply_text(balance_text, parse_mode='Markdown')

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View statistics"""
        stats = self.bot.user_manager.get_user_stats(update.effective_user.id)

        if not stats:
            await update.message.reply_text("❌ Stats not found")
            return

        search_stats = self.bot.search_engine.get_search_statistics(update.effective_user.id)

        stats_text = f"""
📊 **Your Statistics**

**Search Stats:**
• Total Searches: {search_stats['total_searches']}
• Unique Domains: {search_stats['unique_domains']}

**Generation Stats:**
• Total Generations: {stats['total_generations']}

**Daily Usage:**
• Searches: {stats['searches_today']}/{stats['searches_limit']}
• Generations: {stats['generations_today']}/{stats['generations_limit']}
        """

        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def inventory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View inventory"""
        inventories = self.bot.inventory.get_available_inventories()
        inventory_stats = self.bot.inventory.get_inventory_stats()

        if not inventories:
            await update.message.reply_text("❌ No inventory files loaded")
            return

        inv_text = "📂 **Available Inventories**\n\n"

        for inv in inventory_stats['inventories']:
            inv_text += f"📄 {inv['filename']}\n"
            inv_text += f"   • Records: {inv['record_count']}\n"
            inv_text += f"   • Domains: {inv['domain_count']}\n"
            inv_text += f"   • Size: {inv['file_size'] / 1024 / 1024:.2f} MB\n\n"

        inv_text += f"**Total:**\n"
        inv_text += f"• Files: {inventory_stats['total_files']}\n"
        inv_text += f"• Records: {inventory_stats['total_records']}\n"
        inv_text += f"• Domains: {inventory_stats['total_domains']}\n"

        await update.message.reply_text(inv_text, parse_mode='Markdown')

    async def history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View generation history"""
        history = self.bot.db.get_user_generation_history(update.effective_user.id, limit=10)

        if not history:
            await update.message.reply_text("❌ No generation history")
            return

        hist_text = "📜 **Generation History** (Last 10)\n\n"

        for h in history:
            hist_text += f"**{h['domain']}**\n"
            hist_text += f"   • Quantity: {h['quantity']}\n"
            hist_text += f"   • Format: {h['output_format']}\n"
            hist_text += f"   • Generated: {h['results_generated']}\n"
            hist_text += f"   • Time: {h['generation_time']}\n\n"

        await update.message.reply_text(hist_text, parse_mode='Markdown')

    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage settings"""
        settings_text = """
⚙️ **Settings**

Available settings options:
• Default output format
• Default quantity
• Notification preferences

(This feature is under development)
        """

        await update.message.reply_text(settings_text, parse_mode='Markdown')
