from pathlib import Path
from openai import AsyncOpenAI
from docx import Document
from docx.shared import Pt
from pptx import Presentation
from pptx.util import Inches,Pt as PPTPt
from .config import OPENAI_API_KEY,OPENAI_MODEL
Path('output').mkdir(exist_ok=True)
client=AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
async def generate(kind,topic):
    if not client:return f'OPENAI_API_KEY sozlanmagan.\n\n{kind}: {topic}'
    r=await client.chat.completions.create(model=OPENAI_MODEL,messages=[{'role':'system','content':'Sen professional o\'zbek tilidagi ta\'lim AI yordamchisisan.'},{'role':'user','content':f'Vazifa: {kind}\nMavzu: {topic}\nNatijani tabiiy, ravon va tayyor foydalanish mumkin bo\'lgan o\'zbek tilida yoz.'}],temperature=.6);return r.choices[0].message.content or ''
async def answer(q):
    if not client:return 'OPENAI_API_KEY sozlanmagan.'
    r=await client.chat.completions.create(model=OPENAI_MODEL,messages=[{'role':'user','content':q}],temperature=.5);return r.choices[0].message.content or ''
def make_docx(title,body):
    p=Path('output')/(title[:60].replace('/','_')+'.docx');d=Document();d.styles['Normal'].font.name='Times New Roman';d.styles['Normal'].font.size=Pt(12);d.add_heading(title,0);[d.add_paragraph(x) for x in body.splitlines() if x.strip()];d.save(p);return p
def make_pptx(title,body,n=10):
    p=Path('output')/(title[:60].replace('/','_')+'.pptx');r=Presentation();r.slide_width=Inches(13.333);r.slide_height=Inches(7.5);lines=[x for x in body.splitlines() if x.strip()];per=max(1,(len(lines)+n-1)//n)
    for i in range(n):
        c=lines[i*per:(i+1)*per]
        if not c:break
        s=r.slides.add_slide(r.slide_layouts[1]);s.shapes.title.text=title if i==0 else f'{title} — {i+1}';tf=s.placeholders[1].text_frame;tf.clear()
        for j,x in enumerate(c):q=tf.paragraphs[0] if j==0 else tf.add_paragraph();q.text=x;q.font.size=PPTPt(22)
    r.save(p);return p
