import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class AdminHandlers:
    """Admin command handlers"""

    def __init__(self, bot_instance):
        self.bot = bot_instance

    async def check_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return self.bot.db.is_admin(user_id)

    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin panel"""
        if not await self.check_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have admin access")
            return

        panel_text = """
🛠️ **Admin Panel**

Select an action:
        """

        keyboard = [
            [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
            [InlineKeyboardButton("📂 Inventory Management", callback_data="admin_inventory")],
            [InlineKeyboardButton("💰 Credits Management", callback_data="admin_credits")],
            [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
            [InlineKeyboardButton("🔧 Settings", callback_data="admin_settings")],
            [InlineKeyboardButton("📋 Logs", callback_data="admin_logs")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(panel_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def manage_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage users"""
        if not await self.check_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have admin access")
            return

        users_text = """
👥 **User Management**

Options:
/addcredits <user_id> <amount> - Add credits
/removecredits <user_id> <amount> - Remove credits
/banuser <user_id> - Ban user
/unbanuser <user_id> - Unban user
        """

        await update.message.reply_text(users_text, parse_mode='Markdown')

    async def add_credits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add credits to user"""
        if not await self.check_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have admin access")
            return

        if not context.args or len(context.args) < 2:
            await update.message.reply_text("Usage: /addcredits <user_id> <amount>")
            return

        try:
            user_id = int(context.args[0])
            amount = int(context.args[1])

            if self.bot.user_manager.add_credits(user_id, amount, f"Admin grant from {update.effective_user.id}"):
                self.bot.db.log_admin_action(
                    update.effective_user.id,
                    "ADD_CREDITS",
                    f"Added {amount} credits to user {user_id}"
                )
                await update.message.reply_text(f"✅ Added {amount} credits to user {user_id}")
            else:
                await update.message.reply_text("❌ Error adding credits")
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id or amount")

    async def remove_credits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove credits from user"""
        if not await self.check_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have admin access")
            return

        if not context.args or len(context.args) < 2:
            await update.message.reply_text("Usage: /removecredits <user_id> <amount>")
            return

        try:
            user_id = int(context.args[0])
            amount = int(context.args[1])

            if self.bot.user_manager.deduct_credits(user_id, amount, f"Admin removal by {update.effective_user.id}"):
                self.bot.db.log_admin_action(
                    update.effective_user.id,
                    "REMOVE_CREDITS",
                    f"Removed {amount} credits from user {user_id}"
                )
                await update.message.reply_text(f"✅ Removed {amount} credits from user {user_id}")
            else:
                await update.message.reply_text("❌ Error removing credits")
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id or amount")

    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ban user"""
        if not await self.check_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have admin access")
            return

        if not context.args:
            await update.message.reply_text("Usage: /banuser <user_id>")
            return

        try:
            user_id = int(context.args[0])
            if self.bot.db.ban_user(user_id):
                self.bot.db.log_admin_action(
                    update.effective_user.id,
                    "BAN_USER",
                    f"Banned user {user_id}"
                )
                await update.message.reply_text(f"✅ User {user_id} has been banned")
            else:
                await update.message.reply_text("❌ Error banning user")
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id")

    async def unban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unban user"""
        if not await self.check_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have admin access")
            return

        if not context.args:
            await update.message.reply_text("Usage: /unbanuser <user_id>")
            return

        try:
            user_id = int(context.args[0])
            if self.bot.db.unban_user(user_id):
                self.bot.db.log_admin_action(
                    update.effective_user.id,
                    "UNBAN_USER",
                    f"Unbanned user {user_id}"
                )
                await update.message.reply_text(f"✅ User {user_id} has been unbanned")
            else:
                await update.message.reply_text("❌ Error unbanning user")
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id")

    async def reload_inventory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reload inventory"""
        if not await self.check_admin(update.effective_user.id):
            await update.message.reply_text("❌ You don't have admin access")
            return

        loading = await update.message.reply_text("⏳ Reloading inventory...")

        try:
            self.bot.inventory.reload_inventory()
            self.bot.search_engine.clear_cache()

            stats = self.bot.inventory.get_inventory_stats()

            self.bot.db.log_admin_action(
                update.effective_user.id,
                "RELOAD_INVENTORY",
                f"Reloaded {stats['total_files']} files"
            )

            await loading.edit_text(f"""
✅ **Inventory Reloaded**

• Files: {stats['total_files']}
• Records: {stats['total_records']}
• Domains: {stats['total_domains']}
            """, parse_mode='Markdown')
        except Exception as e:
            await loading.edit_text(f"❌ Error: {str(e)}")
