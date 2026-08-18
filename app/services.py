from pathlib import Path

from openai import AsyncOpenAI

from docx import Document
from docx.shared import Pt

from pptx import Presentation
from pptx.util import Inches, Pt as PPTPt

from .config import OPENAI_API_KEY, OPENAI_MODEL


# =========================
# SOZLAMALAR
# =========================

Path("output").mkdir(exist_ok=True)

client = (
    AsyncOpenAI(api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)


# =========================
# AI + WEB SEARCH
# =========================

async def web_ai(prompt: str, use_web: bool = True) -> str:

    if not client:
        return "OPENAI_API_KEY sozlanmagan."

    try:

        tools = []

        if use_web:
            tools = [
                {
                    "type": "web_search",
                    "user_location": {
                        "type": "approximate",
                        "country": "UZ",
                    },
                }
            ]

        response = await client.responses.create(
            model=OPENAI_MODEL,

            instructions=(
                "Sen professional o'zbek tilidagi ta'lim AI yordamchisisan. "
                "Javoblarni tabiiy, ravon, ilmiy va aniq o'zbek tilida yoz. "
                "Agar internet qidiruvi ishlatilgan bo'lsa, "
                "dolzarb ma'lumotlarni ishonchli manbalarga tayangan holda "
                "sintez qil. Noma'lum ma'lumotni o'ylab topma. "
                "Raqamlar va sanalarni imkon qadar tekshir."
            ),

            input=prompt,

            tools=tools,
        )

        return response.output_text or ""

    except Exception as e:

        print("OPENAI ERROR:", repr(e))

        # Web search xato bersa, oddiy AI so'roviga qaytamiz
        if use_web:

            try:

                response = await client.responses.create(
                    model=OPENAI_MODEL,
                    input=prompt,
                )

                return response.output_text or ""

            except Exception as e2:

                print(
                    "OPENAI FALLBACK ERROR:",
                    repr(e2)
                )

        return (
            "AI xizmatida vaqtinchalik xatolik yuz berdi.\n\n"
            "Iltimos, birozdan keyin qayta urinib ko'ring."
        )


# =========================
# HUJJAT GENERATSIYASI
# =========================

async def generate(kind, topic):

    prompt = f"""
Vazifa turi: {kind}

Mavzu:
{topic}

Quyidagi talablar asosida tayyorla:

1. Mavzuni chuqur tahlil qil.
2. Zarur bo'lsa internetdan dolzarb va ishonchli
   ma'lumotlarni qidir.
3. O'zbekiston va mavzuga tegishli rasmiy manbalarga
   imkon qadar ustuvorlik ber.
4. Ilmiy va ta'limiy uslubdan foydalan.
5. Matnni tabiiy, inson yozgandek qilib yoz.
6. Keraksiz takrorlardan qoch.
7. Aniq raqam, sana yoki statistik ma'lumot bo'lsa,
   uni tekshirishga harakat qil.
8. Javobni tayyor foydalanish mumkin bo'lgan
   shaklda yoz.

Agar mavzu kurs ishi, referat, maqola yoki mustaqil ish
bo'lsa, mantiqiy bo'limlar va sarlavhalardan foydalan.

Agar slayd bo'lsa, 10 ta slaydga mos bo'ladigan
mazmunli va qisqa bloklar tayyorla.

Oxirida:

FOYDALANILGAN MANBALAR

bo'limini qo'sh va internetdan foydalanilgan asosiy
manbalarni nomi bilan ko'rsat.
"""

    return await web_ai(
        prompt,
        use_web=True
    )


# =========================
# AI YORDAMCHI
# =========================

async def answer(q):

    prompt = f"""
Foydalanuvchi savoli:

{q}

Savolga aniq, tushunarli va tabiiy o'zbek tilida
javob ber.

Agar savol dolzarb ma'lumot, yangilik, statistik ma'lumot,
narx, sana yoki hozirgi holatga tegishli bo'lsa,
internetdan tekshir.

Agar oddiy tushuntirish talab qilinsa,
keraksiz internet qidiruvi qilma.
"""

    # Oddiy savollarda ham web kerak bo'lishi mumkin,
    # model vaziyatga qarab qidiruvdan foydalanadi.
    return await web_ai(
        prompt,
        use_web=True
    )


# =========================
# DOCX
# =========================

def make_docx(title, body):

    safe_title = (
        title[:60]
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("*", "_")
        .replace("?", "_")
        .replace('"', "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace("|", "_")
    )

    path = (
        Path("output")
        / f"{safe_title}.docx"
    )

    document = Document()

    # Times New Roman 12
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    # Sarlavha
    document.add_heading(
        title,
        0
    )

    # Matn
    for line in body.splitlines():

        line = line.strip()

        if not line:
            continue

        document.add_paragraph(line)

    document.save(path)

    return path


# =========================
# PPTX
# =========================

def make_pptx(title, body, n=10):

    safe_title = (
        title[:60]
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("*", "_")
        .replace("?", "_")
        .replace('"', "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace("|", "_")
    )

    path = (
        Path("output")
        / f"{safe_title}.pptx"
    )

    presentation = Presentation()

    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)

    lines = [
        x.strip()
        for x in body.splitlines()
        if x.strip()
    ]

    if not lines:
        lines = [
            "Ma'lumot topilmadi."
        ]

    per_slide = max(
        1,
        (len(lines) + n - 1) // n
    )

    for i in range(n):

        content = lines[
            i * per_slide:
            (i + 1) * per_slide
        ]

        if not content:
            break

        slide = presentation.slides.add_slide(
            presentation.slide_layouts[1]
        )

        slide.shapes.title.text = (
            title
            if i == 0
            else f"{title} — {i + 1}"
        )

        text_frame = (
            slide.placeholders[1]
            .text_frame
        )

        text_frame.clear()

        for j, line in enumerate(content):

            paragraph = (
                text_frame.paragraphs[0]
                if j == 0
                else text_frame.add_paragraph()
            )

            paragraph.text = line
            paragraph.font.size = PPTPt(22)

    presentation.save(path)

    return path
