from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse

from aiogram import Bot, Dispatcher
from aiogram.types import Update

from .payments import click_callback, payme_callback, payme_auth


app = FastAPI(title="TalabaAI Pro Payments")


# Telegram bot va Dispatcher
_bot: Bot | None = None
_dp: Dispatcher | None = None


def configure_telegram(bot: Bot, dp: Dispatcher):
    global _bot, _dp
    _bot = bot
    _dp = dp


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/payments/success")
async def success():
    return HTMLResponse(
        "<h2>To'lov qabul qilindi. Telegram botga qayting.</h2>"
    )


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if _bot is None or _dp is None:
        raise HTTPException(
            status_code=503,
            detail="Telegram bot hali ishga tushmagan"
        )

    try:
        data = await request.json()
        update = Update.model_validate(data)

        await _dp.feed_update(
            _bot,
            update
        )

        return JSONResponse({"ok": True})

    except Exception as e:
        print(f"TELEGRAM WEBHOOK ERROR: {e}")
        raise HTTPException(
            status_code=500,
            detail="Webhook error"
        )


@app.post("/payments/click")
async def click(request: Request):
    return JSONResponse(
        await click_callback(dict(await request.json()))
    )


@app.post("/payments/payme")
async def payme(request: Request):
    if not payme_auth(
        request.headers.get("Authorization", "")
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    return JSONResponse(
        await payme_callback(await request.json())
    )
