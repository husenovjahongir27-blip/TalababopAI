from pathlib import Path
from openai import AsyncOpenAI
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from pptx import Presentation
from pptx.util import Inches, Pt as PPTPt
from pptx.enum.text import PP_ALIGN

from .config import OPENAI_API_KEY, OPENAI_MODEL

Path("output").mkdir(exist_ok=True)
client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# =========================================================
# AI — PROFESSIONAL AKADEMIK GENERATOR
# =========================================================

BASE_SYSTEM = """
Sen O'zbekistondagi oliy ta'lim talabalari uchun professional
akademik ishlar tayyorlaydigan AI yozuvchisan.

Asosiy maqsad: foydalanuvchi bergan MAVZU bo'yicha mazmunli,
katta hajmli, ilmiy va mantiqan bog'langan matn tayyorlash.

QAT'IY TALABLAR:
- Faqat adabiy va grammatik jihatdan to'g'ri o'zbek tilida yoz.
- Lotin yozuvidan foydalan.
- Bir fikrni boshqa gaplar bilan qayta-qayta takrorlama.
- Har bir paragraf oldingi paragrafni rivojlantirsin.
- Umumiy, bo'sh va mazmunsiz gaplarni ko'paytirma.
- Mavzuga tegishli ilmiy tushunchalar, sabab-oqibatlar,
  tasniflar, jarayonlar, misollar va tahlillarni keng yorit.
- Raqam, sana, statistik ko'rsatkich yoki manbani aniq bilmasang,
  uydirma fakt bermaslikka harakat qil.
- "AI aytishicha", "menimcha", "ushbu topshiriqda" kabi
  xizmatga oid izohlarni yozma.
- Akademik, tabiiy va inson yozgan matnga yaqin uslubdan foydalan.
- Har bir bo'limni bir necha mazmunli paragraf bilan och.
- Hajmni sun'iy takrorlash bilan emas, yangi ilmiy mazmun bilan oshir.
"""

async def _ask(prompt, max_tokens=5000):
    if not client:
        return "OPENAI_API_KEY sozlanmagan."
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": BASE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.55,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


def _clean(text):
    text = text.replace("```text", "").replace("```", "")
    return text.strip()


async def generate(kind, topic, pages=None, template=None, design=None):
    """
    handlers.py bilan mos API.
    Kurs ishi va mustaqil ishda katta hajm uchun matn bir necha
    mantiqiy bloklarda generatsiya qilinadi.
    """

    if not client:
        return "OPENAI_API_KEY sozlanmagan."

    kind_lower = (kind or "").lower().strip()
    pages = int(pages) if pages else None

    # -----------------------------------------------------
    # KURS ISHI
    # -----------------------------------------------------
    if kind_lower == "kurs ishi":
        # Avval reja. Reja keyingi bo'limlarning mantiqiy asosidir.
        outline = await _ask(f"""
MAVZU: {topic}

Shu mavzu bo'yicha kurs ishi uchun aniq ilmiy REJA tuz.

Faqat quyidagi tuzilmani saqla:
I BOB. [katta harflarda bob nomi]
1.1. [kichik harflarda bo'lim]
1.2. [kichik harflarda bo'lim]
1.3. [kichik harflarda bo'lim]

II BOB. [katta harflarda bob nomi]
2.1. [kichik harflarda bo'lim]
2.2. [kichik harflarda bo'lim]
