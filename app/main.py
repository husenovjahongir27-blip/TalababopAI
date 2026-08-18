import asyncio
import uvicorn

from aiogram import Bot, Dispatcher

from .config import BOT_TOKEN, PUBLIC_BASE_URL
from .db import init_db
from .handlers import router
from .web import app, configure_telegram


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN kerak")

    if not PUBLIC_BASE_URL:
        raise RuntimeError("PUBLIC_BASE_URL kerak")

    await init_db()

    bot = Bot(BOT_TOKEN)

    dp = Dispatcher()
    dp.include_router(router)

    # Web serverga bot va dispatcher ulash
    configure_telegram(bot, dp)

    # Telegram webhook manzili
    webhook_url = f"{PUBLIC_BASE_URL}/telegram/webhook"

    await bot.set_webhook(
        webhook_url,
        drop_pending_updates=False,
    )

    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
        )
    )

    try:
        await server.serve()
    finally:
        await bot.delete_webhook()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
