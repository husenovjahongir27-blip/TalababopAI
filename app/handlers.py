from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .config import (
    BOT_NAME,
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
    get_all_user_ids,
)

from .payments import create_payment
from .services import generate, answer, make_docx, make_pptx

router = Router()

waiting = {}
admin_waiting = set()


# =========================================================
# TO‘LOV HOLATLARI
# =========================================================

class PaymentState(StatesGroup):
    waiting_amount = State()
    BOT_NAME,
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
    get_all_user_ids,
)

from .payments import create_payment
from .services import generate, answer, make_docx, make_pptx

router = Router()

waiting = {}

admin_waiting = set()

# =========================================================
# NARXLAR
# =========================================================

SLIDE_PRICES = {
    12: 3000,
    30: 5000,
}

COURSE_PRICES = {
    25: 12000,
    30: 15000,
    40: 25000,
    50: 30000,
    60: 40000,
}

INDEPENDENT_PRICES = {
    15: 5000,
    20: 7000,
    25: 9000,
    30: 11000,
    35: 13000,
    40: 15000,
}

ARTICLE_PRICE = 7000
THESIS_PRICE = 5000
GLOSSARY_PRICE = 4000

# Konspekt: 1 bet = 500 so'm
KONSPEKT_PER_PAGE = 500


# =========================================================
# SLAYD DIZAYNLARI
# =========================================================

SLIDE_DESIGNS = [
    "🎓 Akademik",
    "💼 Professional",
    "✨ Zamonaviy",
    "🧊 Minimal",
    "🌈 Kreativ",
]


# =========================================================
# ASOSIY MENYU
# =========================================================

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


# =========================================================
# INLINE YORDAMCHI
# =========================================================

def inline_buttons(items, prefix):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=str(text),
                    callback_data=f"{prefix}:{value}",
                )
            ]
            for text, value in items
        ]
    )


# =========================================================
# XIZMATLAR
# =========================================================

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


# =========================================================
# START
# =========================================================

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
        f"🤖 {BOT_NAME}\n\n"
        f"🎁 Bepul urinishlar: {user[4]} ta\n"
        f"💰 Balans: {user[3]:,} so'm\n\n"
        f"👇 Kerakli xizmatni tanlang:",
        reply_markup=main_menu(),
    )


# =========================================================
# MENU
# =========================================================

@router.message(Command("menu"))
async def menu(message: Message):

    await ensure_user(message.from_user)

    await message.answer(
        "👇 Xizmatlardan birini tanlang:",
        reply_markup=main_menu(),
    )


# =========================================================
# SLAYD
# =========================================================

@router.message(F.text == "🪄 Slayd yaratish ✨")
async def slide_start(message: Message):

    await ensure_user(message.from_user)

    buttons = [
        ("📓 12 betgacha — 3 000 so'm", "12"),
        ("📓 13–30 bet — 5 000 so'm", "30"),
    ]

    await message.answer(
        "🪄 SLAYD YARATISH\n\n"
        "Avval slayd sonini tanlang:",
        reply_markup=inline_buttons(buttons, "slidepage"),
    )


@router.callback_query(F.data.startswith("slidepage:"))
async def slide_page(callback: CallbackQuery):

    pages = int(callback.data.split(":")[1])

    price = SLIDE_PRICES[pages]

    waiting[callback.from_user.id] = {
        "kind": "Slayd yaratish",
        "file_type": "pptx",
        "pages": pages,
        "price": price,
        "step": "design",
    }

    await callback.answer()

    await callback.message.edit_text(
        f"🪄 Slayd: {pages} betgacha\n"
        f"💰 Narxi: {price:,} so'm\n\n"
        f"🎨 Endi dizaynni tanlang:",
        reply_markup=inline_buttons(
            [(x, x) for x in SLIDE_DESIGNS],
            "slidedesign",
        ),
    )


@router.callback_query(F.data.startswith("slidedesign:"))
async def slide_design(callback: CallbackQuery):

    design = callback.data.split(":", 1)[1]

    data = waiting.get(callback.from_user.id)

    if not data:
        await callback.answer(
            "❌ Buyurtma topilmadi.",
            show_alert=True,
        )
        return

    data["design"] = design
    data["step"] = "topic"

    waiting[callback.from_user.id] = data

    await callback.answer()

    await callback.message.edit_text(
        f"🎨 Tanlangan dizayn: {design}\n\n"
        f"📝 Slayd mavzusini yuboring:",
    )


# =========================================================
# KURS ISHI
# =========================================================

@router.message(F.text == "🎓 Kurs ishi 📑")
async def course_start(message: Message):

    await ensure_user(message.from_user)

    buttons = [
        ("📘 25 bet — 12 000 so'm", "25"),
        ("📘 30 bet — 15 000 so'm", "30"),
        ("📘 40 bet — 25 000 so'm", "40"),
        ("📘 50 bet — 30 000 so'm", "50"),
        ("📘 60 bet — 40 000 so'm", "60"),
    ]

    await message.answer(
        "🎓 KURS ISHI\n\n"
        "Kurs ishi hajmini tanlang:",
        reply_markup=inline_buttons(buttons, "coursepage"),
    )


@router.callback_query(F.data.startswith("coursepage:"))
async def course_page(callback: CallbackQuery):

    pages = int(callback.data.split(":")[1])
    price = COURSE_PRICES[pages]

    waiting[callback.from_user.id] = {
        "kind": "Kurs ishi",
        "file_type": "docx",
        "pages": pages,
        "price": price,
        "step": "topic",
    }

    await callback.answer()

    await callback.message.edit_text(
        f"🎓 Kurs ishi: {pages} bet\n"
        f"💰 Narxi: {price:,} so'm\n\n"
        f"📝 Mavzuni yuboring:",
    )


# =========================================================
# MUSTAQIL ISH
# =========================================================

@router.message(F.text == "📄 Mustaqil ish ✨")
async def independent_start(message: Message):

    await ensure_user(message.from_user)

    buttons = [
        ("📘 15 bet — 5 000 so'm", "15"),
        ("📘 20 bet — 7 000 so'm", "20"),
        ("📘 25 bet — 9 000 so'm", "25"),
        ("📘 30 bet — 11 000 so'm", "30"),
        ("📘 35 bet — 13 000 so'm", "35"),
        ("📘 40 bet — 15 000 so'm", "40"),
    ]

    await message.answer(
        "📄 MUSTAQIL ISH\n\n"
        "Hajmini tanlang:",
        reply_markup=inline_buttons(buttons, "indpage"),
    )


@router.callback_query(F.data.startswith("indpage:"))
async def independent_page(callback: CallbackQuery):

    pages = int(callback.data.split(":")[1])
    price = INDEPENDENT_PRICES[pages]

    waiting[callback.from_user.id] = {
        "kind": "Mustaqil ish",
        "file_type": "docx",
        "pages": pages,
        "price": price,
        "step": "topic",
    }

    await callback.answer()

    await callback.message.edit_text(
        f"📄 Mustaqil ish: {pages} bet\n"
        f"💰 Narxi: {price:,} so'm\n\n"
        f"📝 Mavzuni yuboring:",
    )


# =========================================================
# REFERAT
# =========================================================

@router.message(F.text == "📑 Referat ✨")
async def referat_start(message: Message):

    await ensure_user(message.from_user)

    buttons = [
        ("📘 15 bet — 5 000 so'm", "15"),
        ("📘 20 bet — 7 000 so'm", "20"),
        ("📘 25 bet — 9 000 so'm", "25"),
        ("📘 30 bet — 11 000 so'm", "30"),
        ("📘 35 bet — 13 000 so'm", "35"),
        ("📘 40 bet — 15 000 so'm", "40"),
    ]

    await message.answer(
        "📑 REFERAT\n\n"
        "Hajmini tanlang:",
        reply_markup=inline_buttons(buttons, "refpage"),
    )


@router.callback_query(F.data.startswith("refpage:"))
async def referat_page(callback: CallbackQuery):

    pages = int(callback.data.split(":")[1])
    price = INDEPENDENT_PRICES[pages]

    waiting[callback.from_user.id] = {
        "kind": "Referat",
        "file_type": "docx",
        "pages": pages,
        "price": price,
        "step": "topic",
    }

    await callback.answer()

    await callback.message.edit_text(
        f"📑 Referat: {pages} bet\n"
        f"💰 Narxi: {price:,} so'm\n\n"
        f"📝 Mavzuni yuboring:",
    )


# =========================================================
# KONSPEKT
# =========================================================

@router.message(F.text == "✍️ Konspekt")
async def konspekt_start(message: Message):

    await ensure_user(message.from_user)

    await message.answer(
        "✍️ KONSPEKT\n\n"
        "Necha betlik konspekt kerak?\n\n"
        "💰 Narxi: 500 so'm / bet\n\n"
        "Masalan: 10",
    )

    waiting[message.from_user.id] = {
        "kind": "Konspekt",
        "file_type": "docx",
        "step": "pages",
    }


# =========================================================
# MAQOLA
# =========================================================

@router.message(F.text == "📰 Maqola ✨")
async def article_start(message: Message):

    await ensure_user(message.from_user)

    waiting[message.from_user.id] = {
        "kind": "Maqola",
        "file_type": "docx",
        "pages": None,
        "price": ARTICLE_PRICE,
        "step": "topic",
    }

    await message.answer(
        "📰 MAQOLA\n\n"
        "💰 Narxi: 7 000 so'm\n\n"
        "📝 Mavzuni yuboring:",
    )


# =========================================================
# TEZIS
# =========================================================

@router.message(F.text == "📝 Tezis ✨")
async def thesis_start(message: Message):

    await ensure_user(message.from_user)

    waiting[message.from_user.id] = {
        "kind": "Tezis",
        "file_type": "docx",
        "pages": None,
        "price": THESIS_PRICE,
        "step": "topic",
    }

    await message.answer(
        "📝 TEZIS\n\n"
        "💰 Narxi: 5 000 so'm\n\n"
        "📝 Mavzuni yuboring:",
    )


# =========================================================
# GLOSSARIY
# =========================================================

@router.message(F.text == "💡 Glossariy")
async def glossary_start(message: Message):

    await ensure_user(message.from_user)

    waiting[message.from_user.id] = {
        "kind": "Glossariy",
        "file_type": "docx",
        "pages": None,
        "price": GLOSSARY_PRICE,
        "step": "topic",
    }

    await message.answer(
        "💡 GLOSSARIY\n\n"
        "💰 Narxi: 4 000 so'm\n\n"
        "📝 Mavzuni yuboring:",
    )


# =========================================================
# TEKIN TEST
# =========================================================

@router.message(F.text == "🧪 Test tuzish")
async def test_start(message: Message):

    await ensure_user(message.from_user)

    waiting[message.from_user.id] = {
        "kind": "Test tuzish",
        "file_type": "docx",
        "pages": None,
        "price": 0,
        "free_service": True,
        "step": "topic",
    }

    await message.answer(
        "🧪 TEST TUZISH\n\n"
        "Bu xizmat bepul.\n\n"
        "📝 Mavzuni yuboring:",
    )


# =========================================================
# TEKIN TOOLS
# =========================================================

@router.message(F.text.in_(TOOLS.keys()))
async def choose_tool(message: Message):

    await ensure_user(message.from_user)

    waiting[message.from_user.id] = {
        "kind": TOOLS[message.text],
        "file_type": "docx",
        "price": 0,
        "free_service": True,
        "step": "topic",
    }

    await message.answer(
        "📥 Matn yoki mavzuni yuboring:",
        reply_markup=main_menu(),
    )


# =========================================================
# AI YORDAMCHI — TEKIN
# =========================================================

@router.message(F.text == "🤖 AI yordamchi")
async def ai_helper(message: Message):

    await ensure_user(message.from_user)

    waiting[message.from_user.id] = {
        "kind": "__ai__",
        "file_type": "txt",
        "price": 0,
        "free_service": True,
        "step": "topic",
    }

    await message.answer(
        "🤖 AI yordamchi\n\n"
        "Savolingizni yuboring:",
        reply_markup=main_menu(),
    )


# =========================================================
# PROFIL
# =========================================================

@router.message(F.text == "👤 Profil")
async def profile(message: Message):

    await ensure_user(message.from_user)

    user = await get_user(message.from_user.id)

    await message.answer(
        f"👤 PROFIL\n\n"
        f"🆔 ID: {user[0]}\n"
        f"👤 Username: @{user[1] or 'yo‘q'}\n"
        f"💰 Balans: {user[3]:,} so'm\n"
        f"🎁 Bepul urinishlar: {user[4]} ta",
        reply_markup=main_menu(),
    )


# =========================================================
# TO'LOV HOLATLARI
# =========================================================

class PaymentState(StatesGroup):
    waiting_amount = State()


# =========================================================
# BALANS
# =========================================================

@router.message(F.text == "💰 Balans")
async def balance(message: Message):

    await ensure_user(message.from_user)

    user = await get_user(message.from_user.id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Karta orqali to‘ldirish",
                    callback_data="pay_card",
                )
            ],
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
        f"Joriy balans: {user[3]:,} so‘m\n"
        f"🎁 Bepul: {user[4]}\n\n"
        f"Balansni to‘ldirish usulini tanlang:",
        reply_markup=keyboard,
    )


# =========================================================
# KARTA ORQALI TO'LDIRISH
# =========================================================

@router.callback_query(F.data == "pay_card")
async def pay_card(callback: CallbackQuery):

    await callback.answer()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Chek yuborish",
                    callback_data="card_cheque",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Orqaga",
                    callback_data="back_balance",
                )
            ],
        ]
    )

    await callback.message.answer(
        "💳 PLASTIK KARTA ORQALI BALANSNI TO‘LDIRISH\n\n"

        "1️⃣ TO‘LOV:\n"
        "Quyidagi kartalardan biriga kerakli summani "
        "o‘tkazing.\n\n"

        "🏦 KARTA RAQAMI:\n"
        "<code>5614683113155618</code>\n"
        "👤 Karta egasi: Nilufar Xudoyberdieva\n\n"

        "🏦 KARTA RAQAMI:\n"
        "<code>5614681259285512</code>\n"
        "👤 Karta egasi: Shahzod Alimardanov\n\n"

        "2️⃣ BUYRUQ:\n"
        "To‘lovni amalga oshirgandan so‘ng botga "
        "<code>/chekyubor</code> buyrug‘ini yuboring.\n\n"

        "3️⃣ CHEKNI YUBORING:\n"
        "To‘lov chekini rasm yoki fayl ko‘rinishida yuboring.\n\n"

        "❗️ ESLATMALAR:\n"
        "1. Chek yuborilmasa, balans to‘ldirilmaydi.\n"
        "2. Cheklar administrator tomonidan qo‘lda tekshiriladi.\n"
        "3. Tekshirish biroz vaqt olishi mumkin.\n"
        "4. To‘lov vaqti ko‘rinmasa yoki aniq bo‘lmasa, "
        "to‘lov qabul qilinmaydi.\n\n"

        "Muammo bo‘lsa, bot administratoriga murojaat qiling.",

        reply_markup=keyboard,
        parse_mode="HTML",
    )


# =========================================================
# CHEK YUBORISH
# =========================================================

@router.callback_query(F.data == "card_cheque")
async def card_cheque_start(callback: CallbackQuery):

    await callback.answer()

    await callback.message.answer(
        "📤 CHEK YUBORISH\n\n"
        "To‘lov chekini yuborish uchun:\n\n"
        "1️⃣ <code>/chekyubor</code> buyrug‘ini yuboring.\n"
        "2️⃣ Keyin to‘lov chekini rasm yoki fayl ko‘rinishida yuboring.\n\n"
        "❗️ Chek administrator tomonidan tekshiriladi.\n"
        "Tasdiqlangandan so‘ng balansingiz to‘ldiriladi.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )
    
# =========================================================
# CLICK / PAYME — SUMMA KIRITISH
# =========================================================

@router.callback_query(
    F.data.in_({"pay_click", "pay_payme"})
)
async def payment_callback(
    callback: CallbackQuery,
    state: FSMContext,
):

    provider = (
        "click"
        if callback.data == "pay_click"
        else "payme"
    )

    await state.update_data(provider=provider)
    await state.set_state(PaymentState.waiting_amount)

    await callback.answer()

    await callback.message.answer(
        f"💳 {provider.upper()} ORQALI BALANS TO‘LDIRISH\n\n"
        f"💰 To‘ldirmoqchi bo‘lgan summangizni kiriting.\n\n"
        f"Masalan:\n"
        f"10000\n"
        f"25000\n"
        f"50000\n"
        f"100000\n\n"
        f"❗️ Minimal summa: 1 000 so‘m\n\n"
        f"❌ Bekor qilish: /cancel"
    )


# =========================================================
# CLICK / PAYME — SUMMANI QABUL QILISH
# =========================================================

@router.message(PaymentState.waiting_amount)
async def payment_amount(
    message: Message,
    state: FSMContext,
):

    if message.text == "/cancel":

        await state.clear()

        await message.answer(
            "❌ To‘lov bekor qilindi.",
            reply_markup=main_menu(),
        )

        return

    if not message.text:

        await message.answer(
            "❌ Iltimos, summani raqam bilan kiriting.\n\n"
            "Masalan: 25000"
        )

        return

    # Bo'sh joy va vergullarni olib tashlash
    text = (
        message.text
        .replace(" ", "")
        .replace(",", "")
        .replace(".", "")
    )

    if not text.isdigit():

        await message.answer(
            "❌ Summa noto‘g‘ri.\n\n"
            "Faqat raqam kiriting.\n"
            "Masalan: 25000"
        )

        return

    amount = int(text)

    if amount < 1000:

        await message.answer(
            "❌ Minimal to‘lov: 1 000 so‘m.\n\n"
            "Boshqa summani kiriting:"
        )

        return

    data = await state.get_data()

    provider = data.get("provider")

    if provider not in {"click", "payme"}:

        await state.clear()

        await message.answer(
            "❌ To‘lov tizimi aniqlanmadi.",
            reply_markup=main_menu(),
        )

        return

    try:

        order_id, url = await create_payment(
            message.from_user.id,
            amount,
            provider,
        )

        await state.clear()

        await message.answer(
            f"🧾 BUYURTMA\n\n"
            f"🆔 {order_id}\n"
            f"💰 Summa: {amount:,} so‘m\n"
            f"💳 To‘lov: {provider.upper()}\n\n"
            f"👇 To‘lovni amalga oshirish uchun "
            f"quyidagi havolani bosing:\n\n"
            f"{url}",
            reply_markup=main_menu(),
        )

    except Exception as error:

        print(
            "PAYMENT ERROR:",
            repr(error),
        )

        await state.clear()

        await message.answer(
            "❌ To‘lov xizmatida xatolik yuz berdi.\n"
            "Keyinroq qayta urinib ko‘ring.",
            reply_markup=main_menu(),
        )


# =========================================================
# BALANSGA QAYTISH
# =========================================================

@router.callback_query(F.data == "back_balance")
async def back_balance(callback: CallbackQuery):

    await callback.answer()

    await balance(callback.message)


# =========================================================
# REFERAL
# =========================================================

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


# =========================================================
# TARIX
# =========================================================

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

        text += (
            f"📌 {row[0]}\n"
            f"📝 {row[1][:100]}\n"
            f"📊 {row[2]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=main_menu(),
    )


# =========================================================
# YORDAM
# =========================================================

@router.message(F.text == "ℹ️ Yordam")
async def help_command(message: Message):

    await message.answer(
        "ℹ️ YORDAM\n\n"
        "🪄 Slayd — tanlangan bet va dizaynda\n"
        "📄 Mustaqil ish — tanlangan betda\n"
        "🎓 Kurs ishi — 25–60 bet\n"
        "📑 Referat — 15–40 bet\n"
        "📰 Maqola — 7 000 so'm\n"
        "✍️ Konspekt — 500 so'm/bet\n"
        "📝 Tezis — 5 000 so'm\n"
        "💡 Glossariy — 4 000 so'm\n"
        "🧪 Test — bepul\n"
        "🤖 AI yordamchi — bepul\n"
        "✂️ Qisqartirish — bepul\n"
        "🔄 Qayta yozish — bepul\n"
        "🌐 Tarjima — bepul\n"
        "📋 Reja — bepul\n\n"
        "🎁 Yangi foydalanuvchiga 2 ta bepul "
        "generatsiya beriladi.",
        reply_markup=main_menu(),
    )


# =========================================================
# ADMIN
# =========================================================

@router.message(F.text == "/admin")
async def admin_panel(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Foydalanuvchilar",
                    callback_data="admin_users",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Daromad",
                    callback_data="admin_income",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data="admin_stats",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📨 Xabar yuborish",
                    callback_data="admin_broadcast",
                )
            ],
        ]
    )

    await message.answer(
        "🛠 ADMIN PANEL\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=keyboard,
    )


# =========================================================
# ADMIN — FOYDALANUVCHILAR
# =========================================================

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer(
            "❌ Ruxsat yo‘q.",
            show_alert=True,
        )
        return

    users, jobs, paid = await stats()

    await callback.answer()

    await callback.message.answer(
        f"👥 FOYDALANUVCHILAR\n\n"
        f"Jami foydalanuvchilar: {users} ta"
    )


# =========================================================
# ADMIN — DAROMAD
# =========================================================

@router.callback_query(F.data == "admin_income")
async def admin_income(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer(
            "❌ Ruxsat yo‘q.",
            show_alert=True,
        )
        return

    users, jobs, paid = await stats()

    await callback.answer()

    await callback.message.answer(
        f"💰 DAROMAD\n\n"
        f"Jami tushum: {paid:,} so‘m"
    )


# =========================================================
# ADMIN — STATISTIKA
# =========================================================

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer(
            "❌ Ruxsat yo‘q.",
            show_alert=True,
        )
        return

    users, jobs, paid = await stats()

    await callback.answer()

    await callback.message.answer(
        f"📊 STATISTIKA\n\n"
        f"👥 Foydalanuvchilar: {users} ta\n"
        f"📄 Yaratilgan ishlar: {jobs} ta\n"
        f"💰 Jami daromad: {paid:,} so‘m"
    )


# =========================================================
# ADMIN — XABAR YUBORISH
# =========================================================

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer(
            "❌ Ruxsat yo‘q.",
            show_alert=True,
        )
        return

    admin_waiting.add(callback.from_user.id)

    await callback.answer()

    await callback.message.answer(
        "📨 XABAR YUBORISH\n\n"
        "Barcha foydalanuvchilarga yubormoqchi "
        "bo‘lgan xabaringizni yuboring.\n\n"
        "Matn, rasm yoki boshqa Telegram xabari "
        "bo‘lishi mumkin.\n\n"
        "❌ Bekor qilish: /cancel"
    )


# =========================================================
# ADMIN — XABARNI QABUL QILISH
# =========================================================

@router.message(
    lambda message:
    message.from_user.id in admin_waiting
)
async def admin_broadcast_message(message: Message):

    admin_id = message.from_user.id

    if admin_id not in ADMIN_IDS:
        return

    if message.text == "/cancel":

        admin_waiting.discard(admin_id)

        await message.answer(
            "❌ Xabar yuborish bekor qilindi."
        )

        return

    user_ids = await get_all_user_ids()

    admin_waiting.discard(admin_id)

    status_message = await message.answer(
        f"📨 Xabar yuborilmoqda...\n\n"
        f"👥 Jami: {len(user_ids)} ta"
    )

    sent = 0
    failed = 0

    for user_id in user_ids:

        try:

            await message.bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )

            sent += 1

        except Exception as error:

            print(
                "BROADCAST ERROR:",
                user_id,
                repr(error),
            )

            failed += 1

    try:

        await status_message.edit_text(
            f"✅ Xabar yuborish tugadi.\n\n"
            f"📨 Yuborildi: {sent} ta\n"
            f"❌ Yetkazilmadi: {failed} ta"
        )

    except Exception:
        pass


# =========================================================
# ADMIN — BALANS QO‘SHISH
# =========================================================

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

        await message.answer(
            "❌ ID va summa raqam bo‘lishi kerak."
        )

        return

    user_id = int(parts[1])
    amount = int(parts[2])

    await add_balance(user_id, amount)

    await message.answer(
        f"✅ Balans qo‘shildi.\n\n"
        f"🆔 ID: {user_id}\n"
        f"💰 +{amount:,} so‘m"
    )

# =========================================================
# FOYDALANUVCHI MATNI
# =========================================================

@router.message()
async def process_text(message: Message):

    user_id = message.from_user.id

    if user_id not in waiting:
        return

    data = waiting.get(user_id)

    # -----------------------------------------------------
    # KONSPEKT BET SONI
    # -----------------------------------------------------

    if data.get("step") == "pages":

        if not message.text.isdigit():

            await message.answer(
                "❌ Iltimos, faqat bet sonini yozing.\n"
                "Masalan: 10"
            )

            return

        pages = int(message.text)

        if pages < 1 or pages > 100:

            await message.answer(
                "❌ Bet soni 1 dan 100 gacha bo‘lishi kerak."
            )

            return

        data["pages"] = pages
        data["price"] = pages * KONSPEKT_PER_PAGE
        data["step"] = "topic"

        waiting[user_id] = data

        await message.answer(
            f"✍️ Konspekt: {pages} bet\n"
            f"💰 Narxi: {data['price']:,} so'm\n\n"
            f"📝 Mavzuni yuboring:"
        )

        return

    # -----------------------------------------------------
    # MAVZU
    # -----------------------------------------------------

    waiting.pop(user_id, None)

    kind = data["kind"]
    file_type = data.get("file_type", "docx")
    pages = data.get("pages")
    price = data.get("price", 0)
    design = data.get("design")

    # -----------------------------------------------------
    # AI YORDAMCHI
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # PULLIK / BEPUL XIZMAT
    # -----------------------------------------------------

    free_service = data.get("free_service", False)

    if not free_service:

        allowed = await consume(
            user_id,
            price,
        )

        if not allowed:

            await message.answer(
                "❌ Bepul urinishlaringiz tugagan "
                "yoki balansingiz yetarli emas.\n\n"
                f"💰 Ushbu xizmat narxi: "
                f"{price:,} so'm\n\n"
                f"Balans bo‘limidan hisobingizni "
                f"to‘ldiring.",
                reply_markup=main_menu(),
            )

            return

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    status_message = await message.answer(
        "⏳ Tayyorlanmoqda...\n\n"
        "🤖 AI ishlamoqda..."
    )

    try:

        body = await generate(
            kind,
            message.text,
            pages=pages,
            design=design,
        )

        # -------------------------------------------------
        # PPTX
        # -------------------------------------------------

        if file_type == "pptx":

            slide_count = pages or 10

            path = make_pptx(
                message.text,
                body,
                slide_count,
                design or "🎓 Akademik",
            )

        # -------------------------------------------------
        # DOCX
        # -------------------------------------------------

        else:

            path = make_docx(
                message.text,
                body,
                kind=kind,
                pages=pages,
            )

        await add_job(
            user_id,
            kind,
            message.text,
            "done",
        )

        try:
            await status_message.delete()
        except Exception:
            pass

        await message.answer_document(
            FSInputFile(path),
            caption=(
                f"✅ {kind} tayyor!\n\n"
                f"🤖 {BOT_NAME}"
            ),
            reply_markup=main_menu(),
        )

    except Exception as error:

        print(
            "GENERATION ERROR:",
            repr(error),
        )

        # Agar AI xatolik bersa, pulni qaytarish
        # keyingi bosqichda alohida refund mexanizmi
        # qo‘shish mumkin.

        try:

            await status_message.edit_text(
                "❌ Hujjat yaratishda xatolik yuz berdi.\n"
                "Iltimos, qaytadan urinib ko‘ring."
            )

        except Exception:
            pass

        await message.answer(
            "👇 Menyu:",
            reply_markup=main_menu(),
        )
