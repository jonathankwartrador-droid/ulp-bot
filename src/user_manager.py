import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UserManager:
    """Manage user limits and cooldowns"""

    def __init__(self, db, config: dict):
        self.db = db
        self.config = config
        self.daily_search_limit = config.get('daily_search_limit', 100)
        self.daily_generation_limit = config.get('daily_generation_limit', 50)
        self.cooldown_seconds = config.get('cooldown_seconds', 5)

    def get_or_create_user(self, user_id: int, username: str = None):
        """Get user or create if doesn't exist"""
        user = self.db.get_user(user_id)
        if not user:
            self.db.create_user(user_id, username)
            user = self.db.get_user(user_id)
        return user

    def get_daily_search_count(self, user_id: int) -> int:
        """Get search count for today"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(search_count, 0) FROM daily_limits
            WHERE user_id = ? AND date = CURRENT_DATE
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0

    def get_daily_generation_count(self, user_id: int) -> int:
        """Get generation count for today"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(generation_count, 0) FROM daily_limits
            WHERE user_id = ? AND date = CURRENT_DATE
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0

    def can_search(self, user_id: int) -> tuple:
        """Check if user can perform search"""
        user = self.db.get_user(user_id)
        if not user:
            return False, "User not found"

        if user['is_banned']:
            return False, "You are banned from using this bot"

        search_count = self.get_daily_search_count(user_id)
        if search_count >= self.daily_search_limit:
            return False, f"Daily search limit reached ({self.daily_search_limit})"

        if not self.check_cooldown(user_id, 'search'):
            return False, "Please wait before searching again"

        return True, "OK"

    def can_generate(self, user_id: int, quantity: int = 1) -> tuple:
        """Check if user can perform generation"""
        user = self.db.get_user(user_id)
        if not user:
            return False, "User not found"

        if user['is_banned']:
            return False, "You are banned from using this bot"

        generation_cost = self.config.get('generation_cost', 2)
        total_cost = generation_cost * quantity
        if user['credits'] < total_cost:
            return False, f"Insufficient credits ({user['credits']}/{total_cost})"

        gen_count = self.get_daily_generation_count(user_id)
        if gen_count >= self.daily_generation_limit:
            return False, f"Daily generation limit reached ({self.daily_generation_limit})"

        if not self.check_cooldown(user_id, 'generate'):
            return False, "Please wait before generating again"

        return True, "OK"

    def increment_search_count(self, user_id: int):
        """Increment daily search count"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO daily_limits (user_id, search_count, date)
            VALUES (?, 1, CURRENT_DATE)
            ON CONFLICT(user_id, date) DO UPDATE SET search_count = search_count + 1
        ''', (user_id,))
        conn.commit()
        conn.close()

    def increment_generation_count(self, user_id: int):
        """Increment daily generation count"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO daily_limits (user_id, generation_count, date)
            VALUES (?, 1, CURRENT_DATE)
            ON CONFLICT(user_id, date) DO UPDATE SET generation_count = generation_count + 1
        ''', (user_id,))
        conn.commit()
        conn.close()

    def set_cooldown(self, user_id: int, command: str, seconds: int = None):
        """Set cooldown for user"""
        if seconds is None:
            seconds = self.cooldown_seconds

        cooldown_until = datetime.now() + timedelta(seconds=seconds)

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cooldown (user_id, command, cooldown_until)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, command) DO UPDATE SET cooldown_until = ?
        ''', (user_id, command, cooldown_until, cooldown_until))
        conn.commit()
        conn.close()

    def check_cooldown(self, user_id: int, command: str) -> bool:
        """Check if cooldown is active"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cooldown_until FROM cooldown
            WHERE user_id = ? AND command = ?
        ''', (user_id, command))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return True

        cooldown_until = datetime.fromisoformat(result[0])
        if datetime.now() > cooldown_until:
            return True

        return False

    def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics"""
        user = self.db.get_user(user_id)
        if not user:
            return None

        search_history = self.db.get_user_search_history(user_id)
        generation_history = self.db.get_user_generation_history(user_id)

        search_count_today = self.get_daily_search_count(user_id)
        generation_count_today = self.get_daily_generation_count(user_id)

        return {
            'user_id': user_id,
            'username': user['username'],
            'credits': user['credits'],
            'is_admin': user['is_admin'],
            'is_banned': user['is_banned'],
            'total_searches': user['search_count'],
            'total_generations': user['generation_count'],
            'searches_today': search_count_today,
            'searches_limit': self.daily_search_limit,
            'generations_today': generation_count_today,
            'generations_limit': self.daily_generation_limit,
            'recent_searches': len(search_history),
            'recent_generations': len(generation_history),
            'created_at': user['created_at']
        }

    def deduct_credits(self, user_id: int, amount: int, reason: str = None) -> bool:
        """Deduct credits from user"""
        return self.db.remove_credits(user_id, amount, reason or "Generation")

    def add_credits(self, user_id: int, amount: int, reason: str = None) -> bool:
        """Add credits to user"""
        return self.db.add_credits(user_id, amount, reason or "Admin")
