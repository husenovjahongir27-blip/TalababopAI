from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from .config import (
    BOT_NAME,
    GENERATION_PRICE_UZS,
    REFERRAL_BONUS_UZS,
    ADMIN_IDS,
)
from .db import (
    ensure_user,
    get_user,
    consume,
    add_job,
    history,
    stats,
    add_balance,
)
from .payments import create_payment
from .services import generate, answer, make_docx, make_pptx


router = Router()

waiting = {}


# =========================
# ASOSIY MENYU
# =========================

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🪄 Slayd yaratish ✨"),
                KeyboardButton(text="📄 Mustaqil ish ✨"),
            ],
            [
                KeyboardButton(text="✍️ Konspekt"),
                KeyboardButton(text="📰 Maqola ✨"),
            ],
            [
                KeyboardButton(text="🎓 Kurs ishi 📑"),
                KeyboardButton(text="📑 Referat ✨"),
            ],
            [
                KeyboardButton(text="📝 Tezis ✨"),
                KeyboardButton(text="💡 Glossariy"),
            ],
            [
                KeyboardButton(text="🧪 Test tuzish"),
                KeyboardButton(text="🤖 AI yordamchi"),
            ],
            [
                KeyboardButton(text="✂️ Qisqartirish"),
                KeyboardButton(text="🔄 Qayta yozish"),
            ],
            [
                KeyboardButton(text="🌐 Tarjima"),
                KeyboardButton(text="📋 Reja tuzish"),
            ],
            [
                KeyboardButton(text="👤 Profil"),
                KeyboardButton(text="💰 Balans"),
            ],
            [
                KeyboardButton(text="👥 Referal"),
                KeyboardButton(text="🕘 Tarix"),
            ],
            [
                KeyboardButton(text="ℹ️ Yordam"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
        input_field_placeholder="Menyudan xizmatni tanlang...",
    )


# =========================
# XIZMATLAR
# =========================

KINDS = {
    "🪄 Slayd yaratish ✨": ("Slayd yaratish", "pptx"),
    "📄 Mustaqil ish ✨": ("Mustaqil ish", "docx"),
    "✍️ Konspekt": ("Konspekt", "docx"),
    "📰 Maqola ✨": ("Maqola", "docx"),
    "🎓 Kurs ishi 📑": ("Kurs ishi", "docx"),
    "📑 Referat ✨": ("Referat", "docx"),
    "📝 Tezis ✨": ("Tezis", "docx"),
    "💡 Glossariy": ("Glossariy", "docx"),
    "🧪 Test tuzish": ("Test tuzish", "docx"),
}


TOOLS = {
    "✂️ Qisqartirish": "Matnni qisqartirish",
    "🔄 Qayta yozish": "Matnni tabiiy qayta yozish",
    "🌐 Tarjima": "Tarjima",
    "📋 Reja tuzish": "Reja tuzish",
}


# =========================
# START
# =========================

@router.message(CommandStart())
async def start(message: Message):

    ref = None

    parts = message.text.split(maxsplit=1)

    if (
        len(parts) == 2
        and parts[1].startswith("ref_")
        and parts[1][4:].isdigit()
    ):
        ref = int(parts[1][4:])

    await ensure_user(message.from_user, ref)

    user = await get_user(message.from_user.id)

    await message.answer(
        f"👋 Assalomu alaykum!\n\n"
        f"🤖 {BOT_NAME}\n"
        f"🎁 Bepul: {user[4]}\n"
        f"💰 Balans: {user[3]:,} so'm\n\n"
        f"👇 Menyudan xizmatni tanlang:",
        reply_markup=main_menu(),
    )


# =========================
# MENU
# =========================

@router.message(Command("menu"))
async def menu(message: Message):

    await ensure_user(message.from_user)

    await message.answer(
        "👇 Xizmatlardan birini tanlang:",
        reply_markup=main_menu(),
    )


# =========================
# AI XIZMATLARI
# =========================

@router.message(F.text.in_(KINDS.keys()))
async def choose_service(message: Message):

    await ensure_user(message.from_user)

    waiting[message.from_user.id] = KINDS[message.text]

    await message.answer(
        f"📝 {KINDS[message.text][0]}\n\n"
        f"Mavzuni yuboring:",
        reply_markup=main_menu(),
    )


@router.message(F.text.in_(TOOLS.keys()))
async def choose_tool(message: Message):

    await ensure_user(message.from_user)

    waiting[message.from_user.id] = (
        TOOLS[message.text],
        "docx",
    )

    await message.answer(
        "📥 Matn yoki mavzuni yuboring:",
        reply_markup=main_menu(),
    )


# =========================
# AI YORDAMCHI
# =========================

@router.message(F.text == "🤖 AI yordamchi")
async def ai_helper(message: Message):

    await ensure_user(message.from_user)

    waiting[message.from_user.id] = (
        "__ai__",
        "txt",
    )

    await message.answer(
        "🤖 Savolingizni yuboring:",
        reply_markup=main_menu(),
    )


# =========================
# PROFIL
# =========================

@router.message(F.text == "👤 Profil")
async def profile(message: Message):

    await ensure_user(message.from_user)

    user = await get_user(message.from_user.id)

    await message.answer(
        f"👤 PROFIL\n\n"
        f"🆔 ID: {user[0]}\n"
        f"👤 Username: @{user[1] or 'yo‘q'}\n"
        f"💰 Balans: {user[3]:,} so'm\n"
        f"🎁 Bepul generatsiya: {user[4]}",
        reply_markup=main_menu(),
    )


# =========================
# BALANS
# =========================

@router.message(F.text == "💰 Balans")
async def balance(message: Message):

    await ensure_user(message.from_user)

    user = await get_user(message.from_user.id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Click",
                    callback_data="pay_click",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Payme",
                    callback_data="pay_payme",
                )
            ],
        ]
    )

    await message.answer(
        f"💰 BALANS\n\n"
        f"Joriy balans: {user[3]:,} so'm\n"
        f"🎁 Bepul: {user[4]}\n\n"
        f"1 ta xizmat: {GENERATION_PRICE_UZS:,} so'm\n\n"
        f"To‘lov usulini tanlang:",
        reply_markup=keyboard,
    )


# =========================
# TO‘LOV
# =========================

@router.callback_query(F.data.in_({"pay_click", "pay_payme"}))
async def payment_callback(callback: CallbackQuery):

    provider = (
        "click"
        if callback.data == "pay_click"
        else "payme"
    )

    try:

        order_id, url = await create_payment(
            callback.from_user.id,
            GENERATION_PRICE_UZS,
            provider,
        )

        await callback.answer()

        await callback.message.answer(
            f"🧾 BUYURTMA\n\n"
            f"🆔 {order_id}\n"
            f"💰 Summa: {GENERATION_PRICE_UZS:,} so'm\n"
            f"💳 To‘lov: {provider.upper()}\n\n"
            f"👇 To‘lovni amalga oshirish:\n"
            f"{url}",
            reply_markup=main_menu(),
        )

    except Exception as error:

        print("PAYMENT ERROR:", repr(error))

        await callback.answer(
            "To‘lov xizmatida xatolik.",
            show_alert=True,
        )


# =========================
# REFERAL
# =========================

@router.message(F.text == "👥 Referal")
async def referral(message: Message):

    await ensure_user(message.from_user)

    bot = await message.bot.get_me()

    link = (
        f"https://t.me/{bot.username}"
        f"?start=ref_{message.from_user.id}"
    )

    await message.answer(
        f"👥 REFERAL TIZIMI\n\n"
        f"Har bir referal uchun bonus:\n"
        f"💰 {REFERRAL_BONUS_UZS:,} so'm\n\n"
        f"🔗 Sizning havolangiz:\n"
        f"{link}",
        reply_markup=main_menu(),
    )


# =========================
# TARIX
# =========================

@router.message(F.text == "🕘 Tarix")
async def user_history(message: Message):

    await ensure_user(message.from_user)

    rows = await history(message.from_user.id)

    if not rows:

        await message.answer(
            "🕘 Hozircha foydalanish tarixi mavjud emas.",
            reply_markup=main_menu(),
        )

        return

    text = "🕘 SO‘NGGI XIZMATLAR\n\n"

    for row in rows:

        kind = row[0]
        topic = row[1]
        status = row[2]

        text += (
            f"📌 {kind}\n"
            f"📝 {topic[:100]}\n"
            f"📊 {status}\n\n"
        )

    await message.answer(
        text,
        reply_markup=main_menu(),
    )


# =========================
# YORDAM
# =========================

@router.message(F.text == "ℹ️ Yordam")
async def help_command(message: Message):

    await message.answer(
        "ℹ️ YORDAM\n\n"
        "🪄 Slayd — PowerPoint taqdimot\n"
        "📄 Mustaqil ish — Word hujjat\n"
        "🎓 Kurs ishi — kurs ishi\n"
        "📑 Referat — referat\n"
        "📰 Maqola — ilmiy maqola\n"
        "📝 Tezis — tezis\n"
        "💡 Glossariy — terminlar\n"
        "🧪 Test — test savollari\n"
        "🤖 AI yordamchi — savol-javob\n\n"
        "💰 Balans bo‘limidan Click yoki Payme orqali "
        "to‘lov qilishingiz mumkin.",
        reply_markup=main_menu(),
    )


# =========================
# ADMIN
# =========================

@router.message(F.text == "/admin")
async def admin_panel(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    users, jobs, paid = await stats()

    await message.answer(
        f"🛠 ADMIN PANEL\n\n"
        f"👥 Foydalanuvchilar: {users}\n"
        f"📊 Generatsiyalar: {jobs}\n"
        f"💰 To‘langan: {paid:,} so'm"
    )


@router.message(F.text.startswith("/addbalance "))
async def admin_add_balance(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    parts = message.text.split()

    if len(parts) != 3:
        await message.answer(
            "Format:\n"
            "/addbalance TELEGRAM_ID SUMMA"
        )
        return

    if not parts[1].isdigit() or not parts[2].isdigit():
        await message.answer("❌ ID va summa raqam bo‘lishi kerak.")
        return

    user_id = int(parts[1])
    amount = int(parts[2])

    await add_balance(user_id, amount)

    await message.answer(
        f"✅ Balans qo‘shildi.\n\n"
        f"🆔 ID: {user_id}\n"
        f"💰 +{amount:,} so'm"
    )


# =========================
# FOYDALANUVCHI MATNI
# =========================

@router.message()
async def process_text(message: Message):

    user_id = message.from_user.id

    if user_id not in waiting:
        return

    kind, file_type = waiting.pop(user_id)

    # AI yordamchi
    if kind == "__ai__":

        try:

            result = await answer(message.text)

            await message.answer(
                result,
                reply_markup=main_menu(),
            )

        except Exception as error:

            print("AI ERROR:", repr(error))

            await message.answer(
                "❌ AI xizmatida xatolik yuz berdi.",
                reply_markup=main_menu(),
            )

        return

    # Balans / bepul limitni tekshirish
    allowed = await consume(
        user_id,
        GENERATION_PRICE_UZS,
    )

    if not allowed:

        await message.answer(
            "❌ Bepul limit tugagan yoki balans yetarli emas.\n\n"
            f"💰 1 ta xizmat: {GENERATION_PRICE_UZS:,} so'm\n\n"
            f"Balans bo‘limidan Click yoki Payme orqali "
            f"to‘lov qiling.",
            reply_markup=main_menu(),
        )

        return

    status_message = await message.answer(
        "⏳ Tayyorlanmoqda...\n\n"
        "🤖 AI ishlamoqda..."
    )

    try:

        body = await generate(
            kind,
            message.text,
        )

        if file_type == "pptx":

            path = make_pptx(
                message.text,
                body,
                10,
            )

        else:

            path = make_docx(
                message.text,
                body,
            )

        await add_job(
            user_id,
            kind,
            message.text,
        )

        await status_message.delete()

        await message.answer_document(
            FSInputFile(path),
            caption=(
                f"✅ {kind} tayyor!\n\n"
                f"🤖 {BOT_NAME}"
            ),
            reply_markup=main_menu(),
        )

    except Exception as error:

        print("GENERATION ERROR:", repr(error))

        await status_message.edit_text(
            "❌ Hujjat yaratishda xatolik yuz berdi.\n"
            "Iltimos, qaytadan urinib ko‘ring."
        )

        await message.answer(
            "👇 Menyu:",
            reply_markup=main_menu(),
        )
