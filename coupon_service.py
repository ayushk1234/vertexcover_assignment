import sqlite3
from datetime import datetime, timedelta
from fastapi import HTTPException

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
        print(f"Database error: {error_message}")
        raise HTTPException(
            status_code=500, detail="An error occurred while accessing the database."
        )

    def add_repeat_counts(self, coupon_code, user_total, user_daily, user_weekly, global_total):
        try:
            self.cursor.execute('''
                INSERT INTO coupons (code, user_total, user_daily, user_weekly, global_total)
                VALUES (?, ?, ?, ?, ?)
            ''', (coupon_code, user_total, user_daily, user_weekly, global_total))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Coupon code already exists.")
        except sqlite3.Error as e:
            self.handle_database_error(e)

    def verify_coupon_validity(self, coupon_code, user_id=None):
        try:
            self.cursor.execute('SELECT * FROM coupons WHERE code = ?', (coupon_code,))
            coupon_info = self.cursor.fetchone()

            if not coupon_info:
                raise HTTPException(status_code=404, detail="Coupon code not found.")

            if coupon_info[4] <= 0:
                raise HTTPException(status_code=400, detail="Global repeat count exceeded.")

            if user_id and coupon_info[2] <= 0:
                raise HTTPException(status_code=400, detail="User total repeat count exceeded.")

            if user_id:
                today = datetime.now().strftime('%Y-%m-%d')
                self.cursor.execute('''
                    SELECT COUNT(*) FROM coupon_usage_log
                    WHERE coupon_id = ? AND user_id = ? AND usage_date = ?
                ''', (coupon_info[0], user_id, today))
                user_daily_usage = self.cursor.fetchone()[0]

                if user_daily_usage >= coupon_info[3]:
                    raise HTTPException(status_code=400, detail="User daily repeat count exceeded.")

            if user_id:
                week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
                self.cursor.execute('''
                    SELECT COUNT(*) FROM coupon_usage_log
                    WHERE coupon_id = ? AND user_id = ? AND usage_date >= ?
                ''', (coupon_info[0], user_id, week_start))
                user_weekly_usage = self.cursor.fetchone()[0]

                if user_weekly_usage >= coupon_info[4]:
                    raise HTTPException(status_code=400, detail="User weekly repeat count exceeded.")

            return True, "Coupon code is valid."

        except sqlite3.Error as e:
            self.handle_database_error(e)

    def apply_coupon_code(self, coupon_code, user_id=None):
        try:
            valid, message = self.verify_coupon_validity(coupon_code, user_id)
            if not valid:
                raise HTTPException(status_code=400, detail=message)

            self.cursor.execute('SELECT * FROM coupons WHERE code = ?', (coupon_code,))
            coupon_info = self.cursor.fetchone()

            self.cursor.execute('UPDATE coupons SET global_total = ? WHERE id = ?', (coupon_info[4] - 1, coupon_info[0]))

            if user_id:
                self.cursor.execute('UPDATE coupons SET user_total = ? WHERE id = ?', (coupon_info[2] - 1, coupon_info[0]))

                today = datetime.now().strftime('%Y-%m-%d')
                self.cursor.execute('''
                    INSERT INTO coupon_usage_log (coupon_id, user_id, usage_date)
                    VALUES (?, ?, ?)
                ''', (coupon_info[0], user_id, today))

                week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
                self.cursor.execute('''
                    INSERT INTO coupon_usage_log (coupon_id, user_id, usage_date)
                    VALUES (?, ?, ?)
                ''', (coupon_info[0], user_id, week_start))

            self.conn.commit()
            return True, "Coupon code applied successfully."

        except sqlite3.Error as e:
            self.handle_database_error(e)
