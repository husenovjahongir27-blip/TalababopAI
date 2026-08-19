import aiosqlite
from datetime import datetime

from .config import (
    DB_PATH,
    FREE_GENERATIONS,
    REFERRAL_BONUS_UZS,
)


# =========================
# DATABASE INIT
# =========================

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance INTEGER DEFAULT 0,
                free_left INTEGER DEFAULT 3,
                referral_id INTEGER,
                created_at TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS jobs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                kind TEXT,
                topic TEXT,
                status TEXT,
                created_at TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE,
                user_id INTEGER,
                amount INTEGER,
                provider TEXT,
                status TEXT DEFAULT "pending",
                provider_tx_id TEXT,
                prepare_id TEXT,
                created_at TEXT,
                paid_at TEXT
            )
        """)

        await db.commit()


# =========================
# USER
# =========================

async def ensure_user(user, ref=None):
    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            INSERT OR IGNORE INTO users(
                user_id,
                username,
                first_name,
                free_left,
                referral_id,
                created_at
            )
            VALUES(?,?,?,?,?,?)
            """,
            (
                user.id,
                user.username,
                user.first_name,
                FREE_GENERATIONS,
                ref,
                datetime.utcnow().isoformat(),
            ),
        )

        # Faqat yangi foydalanuvchi qo'shilgan bo'lsa
        # referral bonus beriladi.
        new_user = cursor.rowcount == 1

        if new_user and ref and ref != user.id:
            await db.execute(
                """
                UPDATE users
                SET balance = balance + ?
                WHERE user_id = ?
                """,
                (
                    REFERRAL_BONUS_UZS,
                    ref,
                ),
            )

        # Mavjud foydalanuvchining Telegram ma'lumotlarini
        # yangilab turamiz.
        if not new_user:
            await db.execute(
                """
                UPDATE users
                SET username = ?,
                    first_name = ?
                WHERE user_id = ?
                """,
                (
                    user.username,
                    user.first_name,
                    user.id,
                ),
            )

        await db.commit()


# =========================
# GET USER
# =========================

async def get_user(uid):
    async with aiosqlite.connect(DB_PATH) as db:

        return await (
            await db.execute(
                """
                SELECT *
                FROM users
                WHERE user_id = ?
                """,
                (uid,),
            )
        ).fetchone()


# =========================
# CONSUME BALANCE
# =========================

async def consume(uid, price):
    async with aiosqlite.connect(DB_PATH) as db:

        r = await (
            await db.execute(
                """
                SELECT free_left, balance
                FROM users
                WHERE user_id = ?
                """,
                (uid,),
            )
        ).fetchone()

        if not r:
            return False

        free_left, balance = r

        if free_left > 0:

            await db.execute(
                """
                UPDATE users
                SET free_left = free_left - 1
                WHERE user_id = ?
                """,
                (uid,),
            )

        elif balance >= price:

            await db.execute(
                """
                UPDATE users
                SET balance = balance - ?
                WHERE user_id = ?
                """,
                (
                    price,
                    uid,
                ),
            )

        else:
            return False

        await db.commit()

        return True


# =========================
# ADD BALANCE
# =========================

async def add_balance(uid, amount):
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = ?
            """,
            (
                amount,
                uid,
            ),
        )

        await db.commit()


# =========================
# JOB
# =========================

async def add_job(
    uid,
    kind,
    topic,
    status="done",
):
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            INSERT INTO jobs(
                user_id,
                kind,
                topic,
                status,
                created_at
            )
            VALUES(?,?,?,?,?)
            """,
            (
                uid,
                kind,
                topic,
                status,
                datetime.utcnow().isoformat(),
            ),
        )

        await db.commit()


# =========================
# CREATE ORDER
# =========================

async def create_order(
    oid,
    uid,
    amount,
    provider,
):
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            INSERT INTO orders(
                order_id,
                user_id,
                amount,
                provider,
                created_at
            )
            VALUES(?,?,?,?,?)
            """,
            (
                oid,
                uid,
                amount,
                provider,
                datetime.utcnow().isoformat(),
            ),
        )

        await db.commit()


# =========================
# GET ORDER
# =========================

async def get_order(oid):
    async with aiosqlite.connect(DB_PATH) as db:

        return await (
            await db.execute(
                """
                SELECT
                    order_id,
                    user_id,
                    amount,
                    provider,
                    status,
                    provider_tx_id,
                    prepare_id
                FROM orders
                WHERE order_id = ?
                """,
                (oid,),
            )
        ).fetchone()


# =========================
# PREPARE ORDER
# =========================

async def prepare_order(oid, tx):
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            UPDATE orders
            SET provider_tx_id = ?,
                prepare_id = ?
            WHERE order_id = ?
            """,
            (
                str(tx),
                str(tx),
                oid,
            ),
        )

        await db.commit()


# =========================
# PAY ORDER
# =========================

async def pay_order(oid, tx):
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("BEGIN IMMEDIATE")

        r = await (
            await db.execute(
                """
                SELECT
                    user_id,
                    amount,
                    status
                FROM orders
                WHERE order_id = ?
                """,
                (oid,),
            )
        ).fetchone()

        if not r:
            await db.rollback()
            return "missing"

        user_id, amount, status = r

        # To'lov avval amalga oshirilgan bo'lsa,
        # balansni ikkinchi marta oshirmaymiz.
        if status == "paid":
            await db.commit()
            return "already"

        await db.execute(
            """
            UPDATE orders
            SET status = "paid",
                provider_tx_id = ?,
                paid_at = ?
            WHERE order_id = ?
            """,
            (
                str(tx),
                datetime.utcnow().isoformat(),
                oid,
            ),
        )

        await db.execute(
            """
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = ?
            """,
            (
                amount,
                user_id,
            ),
        )

        await db.commit()

        return "paid"


# =========================
# HISTORY
# =========================

async def history(uid):
    async with aiosqlite.connect(DB_PATH) as db:

        return await (
            await db.execute(
                """
                SELECT
                    kind,
                    topic,
                    status
                FROM jobs
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 10
                """,
                (uid,),
            )
        ).fetchall()


# =========================
# STATISTICS
# =========================

async def stats():
    async with aiosqlite.connect(DB_PATH) as db:

        users = (
            await (
                await db.execute(
                    "SELECT COUNT(*) FROM users"
                )
            ).fetchone()
        )[0]

        jobs = (
            await (
                await db.execute(
                    "SELECT COUNT(*) FROM jobs"
                )
            ).fetchone()
        )[0]

        paid = (
            await (
                await db.execute(
                    """
                    SELECT COALESCE(
                        SUM(amount),
                        0
                    )
                    FROM orders
                    WHERE status = "paid"
                    """
                )
            ).fetchone()
        )[0]

        return users, jobs, paid
        # =========================
# ALL USERS
# =========================

async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        rows = await (
            await db.execute(
                "SELECT user_id FROM users"
            )
        ).fetchall()

        return [row[0] for row in rows]
