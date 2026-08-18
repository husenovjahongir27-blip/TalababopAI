from pathlib import Path
from openai import AsyncOpenAI
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from pptx import Presentation
from pptx.util import Inches, Pt as PPTPt

from .config import OPENAI_API_KEY, OPENAI_MODEL

Path("output").mkdir(exist_ok=True)

client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# =========================================================
# OPENAI
# =========================================================

async def generate(kind, topic, pages=None, template=None, design=None):
    if not client:
        return "OPENAI_API_KEY sozlanmagan."

    extra = ""

    if pages:
        extra += f"\nHajmi: taxminan {pages} bet."

    if template:
        extra += f"\nTanlangan shablon: {template}."

    if design:
        extra += f"\nTanlangan dizayn: {design}."

    if kind.lower() == "kurs ishi":
        instruction = """
Kurs ishini ilmiy va akademik uslubda tayyorla.

Tuzilishi:
1. TITUL VARAQ uchun ma'lumotlar
2. MUNDARIJA
3. KIRISH
4. I BOB
   1.1.
   1.2.
   1.3.
5. II BOB
   2.1.
   2.2.
   2.3.
6. XULOSA
7. FOYDALANILGAN ADABIYOTLAR

Kirishda mavzuning dolzarbligi, maqsadi, vazifalari,
obyekti va predmeti yoritilsin.

Har bir bob mazmunan to'liq va ilmiy bo'lsin.
Matnni sun'iy ravishda takrorlamasdan, mazmunli va
talaba topshirishi mumkin bo'lgan shaklda yoz.
"""
    elif kind.lower() == "mustaqil ish":
        instruction = """
Mustaqil ishni quyidagi tartibda tayyorla:

1. TITUL VARAQ
2. REJA
3. KIRISH
4. ASOSIY QISM
5. XULOSA
6. FOYDALANILGAN ADABIYOTLAR

Mavzu to'liq ochib berilsin.
"""
    elif kind.lower() == "referat":
        instruction = """
Referatni quyidagi ilmiy tartibda tayyorla:

1. TITUL VARAQ
2. REJA
3. KIRISH
4. ASOSIY QISM
5. XULOSA
6. FOYDALANILGAN ADABIYOTLAR

Matn izchil, ilmiy va tushunarli bo'lsin.
"""
    elif kind.lower() == "maqola":
        instruction = """
Ilmiy maqola tayyorla.

Tuzilishi:
- Sarlavha
- Muallif
- Annotatsiya
- Kalit so'zlar
- Kirish
- Adabiyotlar tahlili
- Tadqiqot metodologiyasi
- Natijalar va muhokama
- Xulosa
- Foydalanilgan adabiyotlar

Maqola ilmiy uslubda, mantiqiy va tabiiy yozilsin.
"""
    elif kind.lower() == "tezis":
        instruction = """
Ilmiy tezis tayyorla.

Tuzilishi:
- Sarlavha
- Muallif
- Asosiy mazmun
- Ilmiy natija
- Xulosa
- Kalit so'zlar
- Foydalanilgan manbalar
"""
    elif kind.lower() == "konspekt":
        instruction = """
Mavzu bo'yicha tartibli va mazmunli konspekt tayyorla.
Asosiy tushunchalar, muhim ma'lumotlar va xulosalar
aniq ajratilsin.
"""
    elif kind.lower() == "glossariy":
        instruction = """
Mavzu bo'yicha glossariy tayyorla.
Muhim atamalarni tanla va har biriga qisqa,
aniq va ilmiy ta'rif ber.
"""
    else:
        instruction = """
Vazifani o'zbek tilida professional, tabiiy,
ravon va tayyor foydalanish mumkin bo'lgan
shaklda bajar.
"""

    prompt = f"""
Vazifa turi: {kind}
Mavzu: {topic}
{extra}

{instruction}

Umumiy talablar:
- O'zbek tilida yoz.
- Grammatik xatolarga yo'l qo'yma.
- Mazmunni takrorlama.
- Sarlavha va bo'limlarni aniq ajrat.
- Keraksiz izoh va AI haqida gap yozma.
- Matnni imkon qadar batafsil tayyorla.
"""

    try:
        r = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen professional o'zbek tilidagi "
                        "ta'lim va ilmiy ishlar AI yordamchisisan."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.6,
        )

        return r.choices[0].message.content or ""

    except Exception as e:
        raise e


async def answer(q):
    if not client:
        return "OPENAI_API_KEY sozlanmagan."

    r = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": q,
            }
        ],
        temperature=0.5,
    )

    return r.choices[0].message.content or ""


# =========================================================
# WORD FORMAT
# =========================================================

def setup_document(doc):
    section = doc.sections[0]

    # Akademik hoshiyalar
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)

    style = doc.styles["Normal"]

    style.font.name = "Times New Roman"
    style.font.size = Pt(14)

    # Word uchun shriftning barcha belgilarida
    # Times New Roman ishlatilishini ta'minlash
    style._element.rPr.rFonts.set(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii",
        "Times New Roman",
    )
    style._element.rPr.rFonts.set(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi",
        "Times New Roman",
    )

    pf = style.paragraph_format
    pf.line_spacing = 1.5
    pf.first_line_indent = Cm(1.25)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.space_after = Pt(0)
    pf.space_before = Pt(0)


def add_text_paragraph(doc, text):
    if not text.strip():
        return

    p = doc.add_paragraph()

    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)

    run = p.add_run(text.strip())
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)

    return p


# =========================================================
# TITUL VARAQ
# =========================================================

def add_title_page(doc, title, kind="KURS ISHI"):
    section = doc.sections[0]

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)

    r = p.add_run("GULISTON DAVLAT UNIVERSITETI")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(40)

    r = p.add_run("________________________________")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(30)

    r = p.add_run(kind.upper())
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(40)

    r = p.add_run(title)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)

    for _ in range(4):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    r = p.add_run(
        "Bajardi: ______________________________\n"
        "Tekshirdi: _____________________________"
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)

    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    r = p.add_run("Guliston — 2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)

    doc.add_page_break()


# =========================================================
# DOCX YARATISH
# =========================================================

def make_docx(title, body, kind="hujjat", pages=None):
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

    path = Path("output") / f"{safe_title}.docx"

    doc = Document()
    setup_document(doc)

    # Titul faqat kerakli hujjatlarda
    if kind.lower() in ["kurs ishi", "mustaqil ish", "referat"]:
        add_title_page(
            doc,
            title,
            kind.upper()
        )

    # Asosiy matn
    lines = body.splitlines()

    for line in lines:
        text = line.strip()

        if not text:
            continue

        # Katta sarlavhalarni markazga chiqarish
        upper = text.upper()

        if (
            upper in [
                "KIRISH",
                "XULOSA",
                "MUNDARIJA",
                "FOYDALANILGAN ADABIYOTLAR",
                "ASOSIY QISM",
            ]
            or upper.startswith("I BOB")
            or upper.startswith("II BOB")
        ):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)

            r = p.add_run(text)
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(14)
        else:
            add_text_paragraph(doc, text)

    doc.save(path)

    return path


# =========================================================
# PPTX
# =========================================================

DESIGNS = {
    "🎓 Akademik": {
        "bg": "academic",
        "font": "Times New Roman",
    },
    "💼 Professional": {
        "bg": "professional",
        "font": "Arial",
    },
    "✨ Zamonaviy": {
        "bg": "modern",
        "font": "Aptos",
    },
    "🧊 Minimal": {
        "bg": "minimal",
        "font": "Arial",
    },
    "🌈 Kreativ": {
        "bg": "creative",
        "font": "Aptos",
    },
}


def make_pptx(title, body, n=10, design="🎓 Akademik"):
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

    path = Path("output") / f"{safe_title}.pptx"

    presentation = Presentation()

    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)

    lines = [
        x.strip()
        for x in body.splitlines()
        if x.strip()
    ]

    n = max(1, min(int(n), 30))

    # Matnni tanlangan slayd soniga bo'lish
    per_slide = max(
        1,
        (len(lines) + n - 1) // n
    )

    selected_design = DESIGNS.get(
        design,
        DESIGNS["🎓 Akademik"]
    )

    for i in range(n):
        chunk = lines[
            i * per_slide:
            (i + 1) * per_slide
        ]

        if not chunk:
            break

        slide = presentation.slides.add_slide(
            presentation.slide_layouts[1]
        )

        # Sarlavha
        slide.shapes.title.text = (
            title
            if i == 0
            else f"{title} — {i + 1}"
        )

        title_shape = slide.shapes.title

        for paragraph in title_shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = selected_design["font"]
                run.font.size = PPTPt(28)
                run.font.bold = True

        # Asosiy matn
        text_frame = slide.placeholders[1].text_frame
        text_frame.clear()

        for j, text in enumerate(chunk):
            paragraph = (
                text_frame.paragraphs[0]
                if j == 0
                else text_frame.add_paragraph()
            )

            paragraph.text = text
            paragraph.level = 0

            for run in paragraph.runs:
                run.font.name = selected_design["font"]
                run.font.size = PPTPt(22)

        # Dizayn turi bo'yicha oddiy farqlash
        if selected_design["bg"] == "minimal":
            slide.background.fill.solid()

        elif selected_design["bg"] == "academic":
            slide.background.fill.solid()

        elif selected_design["bg"] == "professional":
            slide.background.fill.solid()

        elif selected_design["bg"] == "modern":
            slide.background.fill.solid()

        elif selected_design["bg"] == "creative":
            slide.background.fill.solid()

    presentation.save(path)

    return path
