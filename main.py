import sqlite3
from datetime import datetime, timedelta

class CouponService:
    def __init__(self):
        try:
            # Create SQLite database and table
            self.conn = sqlite3.connect('coupon_service.db')
            self.cursor = self.conn.cursor()

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS coupons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE,
                    user_total INTEGER,
                    user_daily INTEGER,
                    user_weekly INTEGER,
                    global_total INTEGER
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS coupon_usage_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coupon_id INTEGER,
                    user_id TEXT,
                    usage_date DATE,
                    FOREIGN KEY (coupon_id) REFERENCES coupons (id)
                )
            ''')

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error initializing the database: {e}")

    def handle_database_error(self, error_message):
        """
        Helper method to handle SQLite database errors.
        """
        print(f"Database error: {error_message}")
        return False, "An error occurred while accessing the database."

    def add_repeat_counts(self, coupon_code, user_total, user_daily, user_weekly, global_total):
        """
        Add repeat counts to a coupon code.
        """
        try:
            self.cursor.execute('''
                INSERT INTO coupons (code, user_total, user_daily, user_weekly, global_total)
                VALUES (?, ?, ?, ?, ?)
            ''', (coupon_code, user_total, user_daily, user_weekly, global_total))
            self.conn.commit()
            return True, "Repeat counts added successfully."
        except sqlite3.IntegrityError:
            return False, "Coupon code already exists."
        except sqlite3.Error as e:
            return self.handle_database_error(e)

    def verify_coupon_validity(self, coupon_code, user_id=None):
        """
        Verify the validity of a coupon code based on repeat counts.
        """
        try:
            self.cursor.execute('SELECT * FROM coupons WHERE code = ?', (coupon_code,))
            coupon_info = self.cursor.fetchone()

            if not coupon_info:
                return False, "Coupon code not found."

            # Check global total repeat count
            if coupon_info[4] <= 0:
                return False, "Global repeat count exceeded."

            # Check user total repeat count
            if user_id and coupon_info[2] <= 0:
                return False, "User total repeat count exceeded."

            # Check user daily repeat count
            if user_id:
                today = datetime.now().strftime('%Y-%m-%d')
                self.cursor.execute('''
                    SELECT COUNT(*) FROM coupon_usage_log
                    WHERE coupon_id = ? AND user_id = ? AND usage_date = ?
                ''', (coupon_info[0], user_id, today))
                user_daily_usage = self.cursor.fetchone()[0]

                if user_daily_usage >= coupon_info[3]:
                    return False, "User daily repeat count exceeded."

            # Check user weekly repeat count
            if user_id:
                week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
                self.cursor.execute('''
                    SELECT COUNT(*) FROM coupon_usage_log
                    WHERE coupon_id = ? AND user_id = ? AND usage_date >= ?
                ''', (coupon_info[0], user_id, week_start))
                user_weekly_usage = self.cursor.fetchone()[0]

                if user_weekly_usage >= coupon_info[4]:
                    return False, "User weekly repeat count exceeded."

            return True, "Coupon code is valid."

        except sqlite3.Error as e:
            return self.handle_database_error(e)

    def apply_coupon_code(self, coupon_code, user_id=None):
        """
        Apply a coupon code and update repeat counts accordingly.
        """
        try:
            valid, message = self.verify_coupon_validity(coupon_code, user_id)
            if not valid:
                return False, message

            self.cursor.execute('SELECT * FROM coupons WHERE code = ?', (coupon_code,))
            coupon_info = self.cursor.fetchone()

            # Update global total repeat count
            self.cursor.execute('UPDATE coupons SET global_total = ? WHERE id = ?', (coupon_info[4] - 1, coupon_info[0]))

            # Update user total repeat count
            if user_id:
                self.cursor.execute('UPDATE coupons SET user_total = ? WHERE id = ?', (coupon_info[2] - 1, coupon_info[0]))

                # Update user daily repeat count
                today = datetime.now().strftime('%Y-%m-%d')
                self.cursor.execute('''
                    INSERT INTO coupon_usage_log (coupon_id, user_id, usage_date)
                    VALUES (?, ?, ?)
                ''', (coupon_info[0], user_id, today))

                # Update user weekly repeat count
                week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
                self.cursor.execute('''
                    INSERT INTO coupon_usage_log (coupon_id, user_id, usage_date)
                    VALUES (?, ?, ?)
                ''', (coupon_info[0], user_id, week_start))

            self.conn.commit()
            return True, "Coupon code applied successfully."

        except sqlite3.Error as e:
            return self.handle_database_error(e)

# Example usage:
coupon_service = CouponService()
coupon_service.add_repeat_counts("DISCOUNT50", 3, 1, 1, 10000)

# Applying the coupon code
user_id = "user123"
result, message = coupon_service.apply_coupon_code("DISCOUNT50", user_id)
print(result, message)

# Verifying the coupon code validity
result, message = coupon_service.verify_coupon_validity("DISCOUNT50", user_id)
print(result, message)
