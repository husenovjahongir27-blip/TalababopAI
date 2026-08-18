from aiogram import Router,F
from aiogram.filters import CommandStart
from aiogram.types import Message,CallbackQuery,FSInputFile
from .config import BOT_NAME,GENERATION_PRICE_UZS,REFERRAL_BONUS_UZS,ADMIN_IDS
from .db import ensure_user,get_user,consume,add_job,history,stats,add_balance
from .payments import create_payment
from .services import generate,answer,make_docx,make_pptx
router=Router();waiting={}
KINDS={'🪄 Slayd yaratish ✨':('Slayd yaratish','pptx'),'📄 Mustaqil ish ✨':('Mustaqil ish','docx'),'✍️ Konspekt':('Konspekt','docx'),'📰 Maqola ✨':('Maqola','docx'),'🎓 Kurs ishi 📑':('Kurs ishi','docx'),'📑 Referat ✨':('Referat','docx'),'📝 Tezis ✨':('Tezis','docx'),'💡 Glossariy':('Glossariy','docx'),'🧪 Test tuzish':('Test tuzish','docx')}
TOOLS={'✂️ Qisqartirish':'Matnni qisqartirish','🔄 Qayta yozish':'Matnni tabiiy qayta yozish','🌐 Tarjima':'Tarjima','📋 Reja tuzish':'Reja tuzish'}
@router.message(CommandStart())
async def start(m:Message):
    ref=None;p=m.text.split(maxsplit=1)
    if len(p)==2 and p[1].startswith('ref_') and p[1][4:].isdigit():ref=int(p[1][4:])
    await ensure_user(m.from_user,ref);u=await get_user(m.from_user.id)
    await m.answer(f'👋 Assalomu alaykum!\n\n🤖 {BOT_NAME}\n🎁 Bepul: {u[4]}\n💰 Balans: {u[3]:,} so\'m\n\nMenyudan xizmat tanlang.')
@router.message(F.text.in_(KINDS.keys()))
async def choose(m:Message):waiting[m.from_user.id]=KINDS[m.text];await m.answer('📝 Mavzuni yuboring:')
@router.message(F.text.in_(TOOLS.keys()))
async def tool(m:Message):waiting[m.from_user.id]=(TOOLS[m.text],'docx');await m.answer('📥 Matn yoki mavzuni yuboring:')
@router.message(F.text=='🤖 AI yordamchi')
async def helper(m:Message):waiting[m.from_user.id]=('__ai__','txt');await m.answer('🤖 Savolingizni yuboring:')
@router.message(F.text=='👤 Profil')
async def profile(m:Message):u=await get_user(m.from_user.id);await m.answer(f'👤 Profil\nID: {u[0]}\n💰 {u[3]:,} so\'m\n🎁 Bepul: {u[4]}')
@router.message(F.text=='💰 Balans')
async def balance(m:Message):
    await m.answer(f'💰 Balansni to\'ldirish\n\nSumma: {GENERATION_PRICE_UZS:,} so\'m\n\nClick yoki Payme tugmasini bosib to\'lang.',reply_markup=__import__('aiogram').types.InlineKeyboardMarkup(inline_keyboard=[[__import__('aiogram').types.InlineKeyboardButton(text='💳 Click',callback_data='click')],[__import__('aiogram').types.InlineKeyboardButton(text='💳 Payme',callback_data='payme')]]))
@router.callback_query(F.data.in_({'click','payme'}))
async def pay(c:CallbackQuery):
    oid,url=await create_payment(c.from_user.id,GENERATION_PRICE_UZS,c.data);await c.answer();await c.message.answer(f'🧾 Buyurtma: {oid}\n💰 {GENERATION_PRICE_UZS:,} so\'m\n\nTo\'lov: {url}')
@router.message(F.text=='👥 Referal')
async def ref(m:Message):b=await m.bot.get_me();await m.answer(f'👥 Bonus: {REFERRAL_BONUS_UZS:,} so\'m\nhttps://t.me/{b.username}?start=ref_{m.from_user.id}')
@router.message(F.text=='🕘 Tarix')
async def hist(m:Message):r=await history(m.from_user.id);await m.answer('🕘 Tarix:\n\n'+('\n'.join(f'• {x[0]} — {x[1][:60]}' for x in r) if r else 'Bo\'sh'))
@router.message(F.text=='ℹ️ Yordam')
async def help_(m:Message):await m.answer('ℹ️ Xizmat tanlang → mavzuni yuboring → tayyor faylni oling. Balansni Click/Payme orqali to\'ldiring.')
@router.message(F.text.startswith('/admin'))
async def admin(m:Message):
    if m.from_user.id not in ADMIN_IDS:return
    u,j,p=await stats();await m.answer(f'🛠 ADMIN\nUsers: {u}\nJobs: {j}\nPaid: {p:,} so\'m')
@router.message(F.text.startswith('/addbalance '))
async def addbal(m:Message):
    if m.from_user.id not in ADMIN_IDS:return
    p=m.text.split();
    if len(p)==3 and p[1].isdigit() and p[2].isdigit():await add_balance(int(p[1]),int(p[2]));await m.answer('✅ Balans qo\'shildi.')
@router.message()
async def process(m:Message):
    if m.from_user.id not in waiting:return
    kind,ext=waiting.pop(m.from_user.id)
    if kind=='__ai__':return await m.answer(await answer(m.text))
    if not await consume(m.from_user.id,GENERATION_PRICE_UZS):return await m.answer('❌ Balans yetarli emas. 💰 Balans bo\'limidan Click/Payme orqali to\'lang.')
    s=await m.answer('⏳ Tayyorlanmoqda...')
    try:
        body=await generate(kind,m.text);path=make_pptx(m.text,body,10) if ext=='pptx' else make_docx(m.text,body);await add_job(m.from_user.id,kind,m.text);await s.delete();await m.answer_document(FSInputFile(path));await m.answer('✅ Tayyor!')
    except Exception as e:await s.edit_text('❌ Xatolik yuz berdi.');print(e)
