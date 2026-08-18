import asyncio,uvicorn
from aiogram import Bot,Dispatcher
from .config import BOT_TOKEN
from .db import init_db
from .handlers import router
from .web import app
async def main():
    if not BOT_TOKEN:raise RuntimeError('BOT_TOKEN kerak')
    await init_db();bot=Bot(BOT_TOKEN);dp=Dispatcher();dp.include_router(router)
    await asyncio.gather(dp.start_polling(bot),uvicorn.Server(uvicorn.Config(app,host='0.0.0.0',port=8000)).serve())
if __name__=='__main__':asyncio.run(main())
