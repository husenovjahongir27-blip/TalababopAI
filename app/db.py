import os
from datetime import datetime

import asyncpg

from .config import (
    FREE_GENERATIONS,
    REFERRAL_BONUS_UZS,
)

# =========================================================
# ULANISH (Neon / Supabase kabi bepul Postgres)
# =========================================================
# Render Environment Variables ichiga DATABASE_URL qo'shing.
# Masalan:
# postgresql://user:pass@ep-xxxx.neon.tech/dbname?sslmode=require

DATABASE_URL = os.getenv("DATABASE_URL")

_pool = None


def _parse_dsn():

    dsn = DATABASE_URL
    require_ssl = False

    if dsn and "sslmode=require" in dsn:
        require_ssl = True
        dsn = dsn.split("?")[0]

    return dsn, require_ssl


async def get_pool():

    global _pool

    if _pool is None:

        if not DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL topilmadi. Render'da "
                "Environment Variables ichiga DATABASE_URL "
                "qo'shing (Neon yoki Supabase Postgres manzili)."
            )

        dsn, require_ssl = _parse_dsn()

        _pool = await asyncpg.create_pool(
            dsn=dsn,
            ssl="require" if require_ssl else None,
            min_size=1,
            max_size=5,
        )

    return _pool


# =========================================================
# DATABASE INIT
# =========================================================

async def init_db():

    pool = await get_pool()

    async with pool.acquire() as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance INTEGER DEFAULT 0,
                free_left INTEGER DEFAULT 3,
                referral_id BIGINT,
                created_at TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS jobs(
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                kind TEXT,
                topic TEXT,
                status TEXT,
                created_at TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders(
                id SERIAL PRIMARY KEY,
                order_id TEXT UNIQUE,
                user_id BIGINT,
                amount INTEGER,
                provider TEXT,
                status TEXT DEFAULT 'pending',
                provider_tx_id TEXT,
                prepare_id TEXT,
                created_at TEXT,
                paid_at TEXT
            )
        """)


# =========================================================
# USER
# =========================================================

async def ensure_user(user, ref=None):

    pool = await get_pool()

    async with pool.acquire() as db:

        result = await db.execute(
            """
            INSERT INTO users(
                user_id,
                username,
                first_name,
                free_left,
                referral_id,
                created_at
            )
            VALUES($1,$2,$3,$4,$5,$6)
            ON CONFLICT (user_id) DO NOTHING
            """,
            user.id,
            user.username,
            user.first_name,
            FREE_GENERATIONS,
            ref,
            datetime.utcnow().isoformat(),
        )

        # asyncpg "INSERT 0 1" -> 1 qator qo'shildi (yangi user)
        new_user = result.endswith(" 1")

        # Faqat yangi foydalanuvchiga referral bonus
        # beriladi.
        if new_user and ref and ref != user.id:

            ref_result = await db.execute(
                """
                UPDATE users
                SET balance = balance + $1
                WHERE user_id = $2
                """,
                REFERRAL_BONUS_UZS,
                ref,
            )

            if ref_result.endswith(" 1"):

                print(
                    f"REFERRAL BONUS: "
                    f"{ref} +{REFERRAL_BONUS_UZS} so'm"
                )

        # Foydalanuvchi ma'lumotlarini yangilash
        if not new_user:

            await db.execute(
                """
                UPDATE users
                SET username = $1,
                    first_name = $2
                WHERE user_id = $3
                """,
                user.username,
                user.first_name,
                user.id,
            )


# =========================================================
# GET USER
# =========================================================

async def get_user(uid):

    pool = await get_pool()

    async with pool.acquire() as db:

        return await db.fetchrow(
            """
            SELECT *
            FROM users
            WHERE user_id = $1
            """,
            uid,
        )


# =========================================================
# CONSUME BALANCE
# =========================================================

async def consume(uid, price):

    pool = await get_pool()

    async with pool.acquire() as db:

        r = await db.fetchrow(
            """
            SELECT free_left, balance
            FROM users
            WHERE user_id = $1
            """,
            uid,
        )

        if not r:
            return False

        free_left, balance = r["free_left"], r["balance"]

        # Avval bepul foydalanish
        if free_left > 0:

            await db.execute(
                """
                UPDATE users
                SET free_left = free_left - 1
                WHERE user_id = $1
                """,
                uid,
            )

        # Bepul tugagan bo'lsa balansdan yechish
        elif balance >= price:

            await db.execute(
                """
                UPDATE users
                SET balance = balance - $1
                WHERE user_id = $2
                """,
                price,
                uid,
            )

        else:
            return False

        return True


# =========================================================
# ADD BALANCE
# =========================================================

async def add_balance(uid, amount):

    pool = await get_pool()

    async with pool.acquire() as db:

        await db.execute(
            """
            UPDATE users
            SET balance = balance + $1
            WHERE user_id = $2
            """,
            amount,
            uid,
        )


# =========================================================
# JOB
# =========================================================

async def add_job(
    uid,
    kind,
    topic,
    status="done",
):

    pool = await get_pool()

    async with pool.acquire() as db:

        await db.execute(
            """
            INSERT INTO jobs(
                user_id,
                kind,
                topic,
                status,
                created_at
            )
            VALUES($1,$2,$3,$4,$5)
            """,
            uid,
            kind,
            topic,
            status,
            datetime.utcnow().isoformat(),
        )


# =========================================================
# CREATE ORDER
# =========================================================

async def create_order(
    oid,
    uid,
    amount,
    provider,
):

    pool = await get_pool()

    async with pool.acquire() as db:

        await db.execute(
            """
            INSERT INTO orders(
                order_id,
                user_id,
                amount,
                provider,
                created_at
            )
            VALUES($1,$2,$3,$4,$5)
            """,
            oid,
            uid,
            amount,
            provider,
            datetime.utcnow().isoformat(),
        )


# =========================================================
# GET ORDER
# =========================================================

async def get_order(oid):

    pool = await get_pool()

    async with pool.acquire() as db:

        return await db.fetchrow(
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
            WHERE order_id = $1
            """,
            oid,
        )


# =========================================================
# PREPARE ORDER
# =========================================================

async def prepare_order(oid, tx):

    pool = await get_pool()

    async with pool.acquire() as db:

        await db.execute(
            """
            UPDATE orders
            SET provider_tx_id = $1,
                prepare_id = $2
            WHERE order_id = $3
            """,
            str(tx),
            str(tx),
            oid,
        )


# =========================================================
# REJECT ORDER
# =========================================================

async def reject_order(oid):

    pool = await get_pool()

    async with pool.acquire() as db:

        await db.execute(
            """
            UPDATE orders
            SET status = 'rejected'
            WHERE order_id = $1
            """,
            oid,
        )


# =========================================================
# PAY ORDER
# =========================================================

async def pay_order(oid, tx):

    pool = await get_pool()

    async with pool.acquire() as db:

        async with db.transaction():

            r = await db.fetchrow(
                """
                SELECT
                    user_id,
                    amount,
                    status
                FROM orders
                WHERE order_id = $1
                FOR UPDATE
                """,
                oid,
            )

            if not r:
                return "missing"

            user_id, amount, status = (
                r["user_id"],
                r["amount"],
                r["status"],
            )

            # To'lov avval amalga oshgan bo'lsa,
            # balansni ikkinchi marta oshirmaymiz.
            if status == "paid":
                return "already"

            await db.execute(
                """
                UPDATE orders
                SET status = 'paid',
                    provider_tx_id = $1,
                    paid_at = $2
                WHERE order_id = $3
                """,
                str(tx),
                datetime.utcnow().isoformat(),
                oid,
            )

            await db.execute(
                """
                UPDATE users
                SET balance = balance + $1
                WHERE user_id = $2
                """,
                amount,
                user_id,
            )

        return "paid"


# =========================================================
# HISTORY
# =========================================================

async def history(uid):

    pool = await get_pool()

    async with pool.acquire() as db:

        return await db.fetch(
            """
            SELECT
                kind,
                topic,
                status
            FROM jobs
            WHERE user_id = $1
            ORDER BY id DESC
            LIMIT 10
            """,
            uid,
        )


# =========================================================
# STATISTICS
# =========================================================

async def stats():

    pool = await get_pool()

    async with pool.acquire() as db:

        users = await db.fetchval(
            "SELECT COUNT(*) FROM users"
        )

        jobs = await db.fetchval(
            "SELECT COUNT(*) FROM jobs"
        )

        paid = await db.fetchval(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM orders
            WHERE status = 'paid'
            """
        )

        return users, jobs, paid


# =========================================================
# ALL USERS
# =========================================================

async def get_all_user_ids():

    pool = await get_pool()

    async with pool.acquire() as db:

        rows = await db.fetch(
            "SELECT user_id FROM users"
        )

        return [row["user_id"] for row in rows]
