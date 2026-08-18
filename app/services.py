from pathlib import Path

from openai import AsyncOpenAI

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

from pptx import Presentation
from pptx.util import Inches, Pt as PPTPt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from .config import OPENAI_API_KEY, OPENAI_MODEL


Path("output").mkdir(exist_ok=True)

client = (
    AsyncOpenAI(api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)


# =========================================================
# AI
# =========================================================

async def generate(
    kind,
    topic,
    pages=None,
    template=None,
    design=None,
):
    if not client:
        return "OPENAI_API_KEY sozlanmagan."

    extra = ""

    if pages:
        extra += f"""
Hujjat hajmi: {pages} bet.
Hajmni mazmunni takrorlash yoki keraksiz cho'zish orqali emas,
mazmunli va to'liq ilmiy material orqali ta'minla.
"""

    if template:
        extra += f"""
Tanlangan shablon: {template}.
"""

    if design:
        extra += f"""
Tanlangan slayd dizayni: {design}.
"""

    kind_lower = kind.lower()

    if kind_lower == "kurs ishi":
        instruction = """
KURS ISHI TAYYORLA.

Tuzilishi:

1. TITUL VARAQ
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

Kirishda:
- mavzuning dolzarbligi;
- tadqiqot maqsadi;
- tadqiqot vazifalari;
- tadqiqot obyekti;
- tadqiqot predmeti
yoritilsin.

Har bir bobda 3 ta mazmunli bo'lim bo'lsin.

Ilmiy uslubdan foydalan.
Mavzuni to'liq ochib ber.
Bir xil gaplarni takrorlama.
"""

    elif kind_lower == "mustaqil ish":
        instruction = """
MUSTAQIL ISH TAYYORLA.

Tuzilishi:

1. TITUL VARAQ
2. REJA
3. KIRISH
4. ASOSIY QISM
5. XULOSA
6. FOYDALANILGAN ADABIYOTLAR

Mavzu to'liq va izchil yoritilsin.
"""

    elif kind_lower == "referat":
        instruction = """
REFERAT TAYYORLA.

Tuzilishi:

1. TITUL VARAQ
2. REJA
3. KIRISH
4. ASOSIY QISM
5. XULOSA
6. FOYDALANILGAN ADABIYOTLAR

Ilmiy va tushunarli uslubdan foydalan.
"""

    elif kind_lower == "maqola":
        instruction = """
ILMIY MAQOLA TAYYORLA.

Tuzilishi:

Sarlavha
Muallif
Annotatsiya
Kalit so'zlar
Kirish
Adabiyotlar tahlili
Tadqiqot metodologiyasi
Natijalar va muhokama
Xulosa
Foydalanilgan adabiyotlar

Maqola ilmiy maqola talablariga mos,
mantiqiy va tabiiy yozilsin.
"""

    elif kind_lower == "tezis":
        instruction = """
ILMIY TEZIS TAYYORLA.

Tuzilishi:

Sarlavha
Muallif
Asosiy mazmun
Ilmiy natijalar
Xulosa
Kalit so'zlar
Foydalanilgan manbalar
"""

    elif kind_lower == "konspekt":
        instruction = """
MAVZU BO'YICHA KONSPEKT TAYYORLA.

Muhim tushunchalar,
asosiy fikrlar,
faktlar,
ta'riflar
va xulosalarni tartibli joylashtir.
"""

    elif kind_lower == "glossariy":
        instruction = """
MAVZU BO'YICHA GLOSSARIY TAYYORLA.

Muhim ilmiy atamalarni tanla.
Har bir atamaga aniq, qisqa va ilmiy ta'rif ber.
"""

    else:
        instruction = """
Vazifani professional, tabiiy va ravon
o'zbek tilida bajar.
"""

    prompt = f"""
Sen professional o'zbek tilidagi
ta'lim va ilmiy ishlar AI yordamchisisan.

Vazifa turi:
{kind}

Mavzu:
{topic}

{extra}

{instruction}

Umumiy talablar:

- O'zbek tilida yoz.
- Grammatik jihatdan to'g'ri yoz.
- Tabiiy inson yozganidek bo'lsin.
- Bir xil fikrlarni takrorlama.
- Keraksiz AI izohlarini yozma.
- Sarlavhalarni aniq ajrat.
- Mavzudan chetga chiqma.
- Imkon qadar mazmunli va batafsil yoz.
"""

    response = await client.chat.completions.create(
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

    return response.choices[0].message.content or ""


async def answer(q):
    if not client:
        return "OPENAI_API_KEY sozlanmagan."

    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": q,
            }
        ],
        temperature=0.5,
    )

    return response.choices[0].message.content or ""


# =========================================================
# WORD
# =========================================================

def setup_document(doc):

    section = doc.sections[0]

    # Hoshiyalar
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)

    style = doc.styles["Normal"]

    style.font.name = "Times New Roman"
    style.font.size = Pt(14)

    # Times New Roman
    rpr = style._element.get_or_add_rPr()
    rfonts = rpr.rFonts

    if rfonts is not None:
        rfonts.set(
            "{http://schemas.openxmlformats.org/"
            "wordprocessingml/2006/main}ascii",
            "Times New Roman",
        )
        rfonts.set(
            "{http://schemas.openxmlformats.org/"
            "wordprocessingml/2006/main}hAnsi",
            "Times New Roman",
        )

    paragraph = style.paragraph_format

    paragraph.line_spacing = 1.5
    paragraph.first_line_indent = Cm(1.25)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.space_before = Pt(0)
    paragraph.space_after = Pt(0)


def add_text_paragraph(doc, text):

    if not text.strip():
        return

    p = doc.add_paragraph()

    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)

    run = p.add_run(text.strip())

    run.font.name = "Times New Roman"
    run.font.size = Pt(14)

    return p


def add_heading(doc, text):

    p = doc.add_paragraph()

    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)

    run = p.add_run(text.strip())

    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)

    return p


# =========================================================
# TITUL
# =========================================================

def add_title_page(doc, title, kind):

    p = doc.add_paragraph()

    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    r = p.add_run(
        "GULISTON DAVLAT UNIVERSITETI"
    )

    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)

    for _ in range(2):
        doc.add_paragraph()

    p = doc.add_paragraph()

    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    r = p.add_run(kind.upper())

    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)

    for _ in range(2):
        doc.add_paragraph()

    p = doc.add_paragraph()

    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    r = p.add_run(title)

    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)

    for _ in range(5):
        doc.add_paragraph()

    p = doc.add_paragraph()

    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    r = p.add_run(
        "Bajardi: ______________________________\n"
        "Tekshirdi: _____________________________"
    )

    r.font.name = "Times New Roman"
    r.font.size = Pt(14)

    for _ in range(4):
        doc.add_paragraph()

    p = doc.add_paragraph()

    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    r = p.add_run("Guliston — 2026")

    r.font.name = "Times New Roman"
    r.font.size = Pt(14)

    doc.add_page_break()


# =========================================================
# DOCX
# =========================================================

def make_docx(
    title,
    body,
    kind="hujjat",
    pages=None,
):

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

    # Titul
    if kind.lower() in [
        "kurs ishi",
        "mustaqil ish",
        "referat",
    ]:
        add_title_page(
            doc,
            title,
            kind,
        )

    lines = body.splitlines()

    for line in lines:

        text = line.strip()

        if not text:
            continue

        upper = text.upper()

        is_heading = (
            upper in [
                "KIRISH",
                "XULOSA",
                "MUNDARIJA",
                "ASOSIY QISM",
                "FOYDALANILGAN ADABIYOTLAR",
            ]
            or upper.startswith("I BOB")
            or upper.startswith("II BOB")
            or upper.startswith("1.")
            or upper.startswith("2.")
        )

        if is_heading:
            add_heading(
                doc,
                text,
            )
        else:
            add_text_paragraph(
                doc,
                text,
            )

    doc.save(path)

    return path


# =========================================================
# SLAYD DIZAYNLARI
# =========================================================

DESIGNS = {
    "🎓 Akademik": {
        "font": "Times New Roman",
        "title_size": 30,
        "body_size": 21,
    },

    "💼 Professional": {
        "font": "Arial",
        "title_size": 30,
        "body_size": 21,
    },

    "✨ Zamonaviy": {
        "font": "Aptos",
        "title_size": 32,
        "body_size": 22,
    },

    "🧊 Minimal": {
        "font": "Arial",
        "title_size": 28,
        "body_size": 20,
    },

    "🌈 Kreativ": {
        "font": "Aptos",
        "title_size": 32,
        "body_size": 22,
    },
}


# =========================================================
# SLAYD
# =========================================================

def make_pptx(
    title,
    body,
    n=10,
    design="🎓 Akademik",
):

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

    n = max(
        1,
        min(int(n), 30),
    )

    # Agar AI kam matn qaytarsa,
    # mavjud matnni keraksiz takrorlamaymiz.
    per_slide = max(
        1,
        (len(lines) + n - 1) // n,
    )

    selected = DESIGNS.get(
        design,
        DESIGNS["🎓 Akademik"],
    )

    for i in range(n):

        chunk = lines[
            i * per_slide:
            (i + 1) * per_slide
        ]

        if not chunk:
            break

        slide = presentation.slides.add_slide(
            presentation.slide_layouts[6]
        )

        # -------------------------
        # TITLE
        # -------------------------

        title_box = slide.shapes.add_textbox(
            Inches(0.7),
            Inches(0.4),
            Inches(11.9),
            Inches(1.0),
        )

        title_frame = title_box.text_frame

        title_frame.clear()

        paragraph = title_frame.paragraphs[0]

        paragraph.alignment = PP_ALIGN.CENTER

        run = paragraph.add_run()

        run.text = (
            title
            if i == 0
            else f"{title} — {i + 1}"
        )

        run.font.name = selected["font"]
        run.font.size = PPTPt(
            selected["title_size"]
        )
        run.font.bold = True

        # -------------------------
        # BODY
        # -------------------------

        body_box = slide.shapes.add_textbox(
            Inches(1.0),
            Inches(1.7),
            Inches(11.3),
            Inches(5.0),
        )

        frame = body_box.text_frame

        frame.clear()

        frame.word_wrap = True

        for j, text in enumerate(chunk):

            paragraph = (
                frame.paragraphs[0]
                if j == 0
                else frame.add_paragraph()
            )

            paragraph.text = text

            paragraph.level = 0

            paragraph.space_after = PPTPt(10)

            for run in paragraph.runs:

                run.font.name = selected["font"]

                run.font.size = PPTPt(
                    selected["body_size"]
                )

        # -------------------------
        # SLIDE NUMBER
        # -------------------------

        number_box = slide.shapes.add_textbox(
            Inches(12.0),
            Inches(6.8),
            Inches(0.7),
            Inches(0.4),
        )

        number_frame = number_box.text_frame

        number_frame.clear()

        number_paragraph = (
            number_frame.paragraphs[0]
        )

        number_paragraph.alignment = PP_ALIGN.RIGHT

        number_run = (
            number_paragraph.add_run()
        )

        number_run.text = str(i + 1)

        number_run.font.name = selected["font"]
        number_run.font.size = PPTPt(12)

    presentation.save(path)

    return path
