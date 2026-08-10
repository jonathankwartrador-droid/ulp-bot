import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

# States for conversation handlers
SEARCH_DOMAIN, SELECT_INVENTORY, SELECT_EXACT = range(3)
GEN_DOMAIN, GEN_INVENTORY, GEN_QUANTITY, GEN_FORMAT, GEN_CONFIRM = range(5)


class InlineHandlers:
    """Inline query and callback handlers"""

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.user_state = {}

    async def start_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start domain search"""
        query = update.callback_query
        user_id = query.from_user.id

        can_search, message = self.bot.user_manager.can_search(user_id)
        if not can_search:
            await query.answer(message, show_alert=True)
            return

        await query.edit_message_text("🔍 Enter domain to search:")
        self.user_state[user_id] = {'action': 'search_domain'}
        return SEARCH_DOMAIN

    async def search_domain_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process domain search input"""
        user_id = update.effective_user.id
        domain = update.message.text.strip()

        can_search, message = self.bot.user_manager.can_search(user_id)
        if not can_search:
            await update.message.reply_text(f"❌ {message}")
            return ConversationHandler.END

        search_result = self.bot.search_engine.search(domain, user_id=user_id)

        if not search_result['success']:
            await update.message.reply_text(f"❌ Search error: {search_result.get('error', 'Unknown error')}")
            return ConversationHandler.END

        results_count = search_result['count']
        cached_info = " (cached)" if search_result['cached'] else ""

        if results_count == 0:
            await update.message.reply_text(f"❌ No results found for: {domain}{cached_info}")
            return ConversationHandler.END

        self.bot.user_manager.increment_search_count(user_id)
        self.bot.user_manager.set_cooldown(user_id, 'search')

        results_text = f"""
✅ **Search Results**

Domain: `{domain}`
Results: {results_count}{cached_info}

Select action:
        """

        keyboard = [
            [InlineKeyboardButton("📋 Generate Credentials", callback_data=f"gen_{domain}")],
            [InlineKeyboardButton("🔍 New Search", callback_data="search")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(results_text, reply_markup=reply_markup, parse_mode='Markdown')

        context.user_data['search_results'] = search_result['results']
        context.user_data['current_domain'] = domain

        return ConversationHandler.END

    async def start_generate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start credential generation"""
        query = update.callback_query
        user_id = query.from_user.id

        can_gen, message = self.bot.user_manager.can_generate(user_id)
        if not can_gen:
            await query.answer(message, show_alert=True)
            return

        domain = query.data.split('_', 1)[1]
        inventories = self.bot.inventory.get_available_inventories()

        if not inventories:
            await query.answer("❌ No inventory files available", show_alert=True)
            return

        inv_text = f"📂 Select inventory for: `{domain}`\n\n"

        keyboard = []
        for inv_file in inventories:
            keyboard.append([InlineKeyboardButton(
                inv_file,
                callback_data=f"gen_inv_{domain}_{inv_file}"
            )])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(inv_text, reply_markup=reply_markup, parse_mode='Markdown')

        context.user_data['gen_domain'] = domain
        return GEN_INVENTORY

    async def select_inventory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select inventory for generation"""
        query = update.callback_query
        user_id = query.from_user.id

        data_parts = query.data.split('_', 3)
        domain = data_parts[2]
        inventory_file = data_parts[3]

        qty_text = f"""
📋 **Generate Credentials**

Domain: `{domain}`
Inventory: `{inventory_file}`

Enter quantity (1-50):
        """

        keyboard = [
            [
                InlineKeyboardButton("1", callback_data=f"qty_1_{domain}_{inventory_file}"),
                InlineKeyboardButton("5", callback_data=f"qty_5_{domain}_{inventory_file}"),
                InlineKeyboardButton("10", callback_data=f"qty_10_{domain}_{inventory_file}")
            ],
            [
                InlineKeyboardButton("25", callback_data=f"qty_25_{domain}_{inventory_file}"),
                InlineKeyboardButton("50", callback_data=f"qty_50_{domain}_{inventory_file}")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(qty_text, reply_markup=reply_markup, parse_mode='Markdown')

        context.user_data['gen_domain'] = domain
        context.user_data['gen_inventory'] = inventory_file

        return GEN_QUANTITY

    async def select_quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select quantity and format"""
        query = update.callback_query

        data_parts = query.data.split('_')
        quantity = int(data_parts[1])
        domain = data_parts[2]
        inventory_file = data_parts[3]

        fmt_text = f"""
📋 **Select Output Format**

Domain: `{domain}`
Quantity: {quantity}
Inventory: `{inventory_file}`

Choose format:
        """

        keyboard = [
            [InlineKeyboardButton("WITH_URL (domain:login:pass)", callback_data=f"fmt_WITH_URL_{quantity}_{domain}_{inventory_file}")],
            [InlineKeyboardButton("WITHOUT_URL (login:pass)", callback_data=f"fmt_WITHOUT_URL_{quantity}_{domain}_{inventory_file}")],
            [InlineKeyboardButton("URL_ONLY", callback_data=f"fmt_URL_ONLY_{quantity}_{domain}_{inventory_file}")],
            [InlineKeyboardButton("LOGIN_ONLY", callback_data=f"fmt_LOGIN_ONLY_{quantity}_{domain}_{inventory_file}")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(fmt_text, reply_markup=reply_markup, parse_mode='Markdown')

        return GEN_FORMAT

    async def confirm_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm and perform generation"""
        query = update.callback_query
        user_id = query.from_user.id

        data_parts = query.data.split('_', 4)
        output_format = data_parts[1]
        quantity = int(data_parts[2])
        domain = data_parts[3]
        inventory_file = data_parts[4]

        generation_cost = self.bot.config.get('generation_cost', 2)
        total_cost = generation_cost * quantity
        user = self.bot.db.get_user(user_id)

        if user['credits'] < total_cost:
            await query.answer(f"❌ Insufficient credits ({user['credits']}/{total_cost})", show_alert=True)
            return

        if 'search_results' not in context.user_data:
            search_result = self.bot.search_engine.search(domain)
            if not search_result['success']:
                await query.answer("❌ Error searching domain", show_alert=True)
                return
            results = search_result['results']
        else:
            results = context.user_data['search_results']

        results = [r for r in results if r.domain and r.domain.lower() == domain.lower()]

        if not results:
            await query.answer("❌ No results found for this domain", show_alert=True)
            return

        from src.generator import CredentialGenerator
        generated = CredentialGenerator.generate(
            results,
            quantity=quantity,
            output_format=output_format,
            random_selection=True
        )

        if not generated:
            await query.answer("❌ Error generating credentials", show_alert=True)
            return

        self.bot.user_manager.deduct_credits(user_id, total_cost, f"Generate {quantity} credentials for {domain}")
        self.bot.user_manager.increment_generation_count(user_id)
        self.bot.user_manager.set_cooldown(user_id, 'generate')

        self.bot.db.add_generation_history(
            user_id,
            domain,
            quantity,
            output_format,
            inventory_file,
            len(generated)
        )

        export_result = self.bot.export_manager.export_credentials(generated, domain, user_id)

        if export_result['success']:
            gen_text = f"""
✅ **Credentials Generated!**

Domain: `{domain}`
Format: {output_format}
Generated: {len(generated)}/{quantity}
Cost: {total_cost} credits
Remaining: {user['credits'] - total_cost} credits

📁 File: `{export_result['filename']}`
            """

            keyboard = [
                [InlineKeyboardButton("🔍 New Search", callback_data="search")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(gen_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.edit_message_text(f"⚠️ Generated but export failed: {export_result.get('error')}")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()

        if query.data == "search":
            return await self.start_search(update, context)
        elif query.data == "generate":
            await query.edit_message_text("🔍 Enter domain to generate for:")
            return SEARCH_DOMAIN
        elif query.data == "balance":
            await self.bot.user_handlers.balance(update, context)
        elif query.data == "stats":
            await self.bot.user_handlers.stats(update, context)
        elif query.data == "history":
            await self.bot.user_handlers.history(update, context)
        elif query.data == "settings":
            await self.bot.user_handlers.settings(update, context)
        elif query.data.startswith("gen_"):
            return await self.start_generate(update, context)
