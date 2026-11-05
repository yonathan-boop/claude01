@'
import os
import sys
import copy
import io
import re
import docx
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

master_path = r"\\192.168.195.7\Methodist-11 Document\SOAL UJIAN\Soal Ujian Semester I T.P.2026-2027\SD SWASTA METHODIST.docx"
src_p = r"\\192.168.195.7\Methodist-11 Document\SOAL UJIAN\Soal Ujian Semester I T.P.2026-2027\Bahasa Inggris\Bahasa Inggris 5 Linda.docx"
output_path = r"C:\Users\yonat\AppData\Local\Temp\test_bi5_2pages.docx"

doc = docx.Document(master_path)
src_doc = docx.Document(src_p)

# 1. Update Kop Surat
t0 = doc.tables[0]
for t in t0.rows[0].cells[4]._tc.iter(qn('w:t')): t.text = "B. Inggris"
for t in t0.rows[1].cells[4]._tc.iter(qn('w:t')): t.text = "Kamis, 3 Desember 2026"
for t in t0.rows[2].cells[4]._tc.iter(qn('w:t')): t.text = "VA SD"
for t in t0.rows[3].cells[4]._tc.iter(qn('w:t')): t.text = " " * 17 + "/ "

body = doc._body._element
body.remove(doc.tables[1]._tbl)
for p in list(doc.paragraphs):
    body.remove(p._p)

final_sect = body.find(qn('w:sectPr'))
if final_sect is not None:
    body.remove(final_sect)

F4_W = 12242
F4_H = 18722
MARGIN_TOP = 284     # 0.50 cm
MARGIN_BOTTOM = 340  # 0.60 cm
MARGIN_LEFT = 567    # 1.00 cm
MARGIN_RIGHT = 567   # 1.00 cm
COL_SPACING = 567    # 1.00 cm

def make_sectPr(cols=1):
    col_str = f'<w:cols {nsdecls("w")} w:num="{cols}" w:space="{COL_SPACING}"/>' if cols > 1 else f'<w:cols {nsdecls("w")} w:space="720"/>'
    return parse_xml(f'''
    <w:sectPr {nsdecls("w")}>
      <w:type w:val="continuous"/>
      <w:pgSz w:w="{F4_W}" w:h="{F4_H}" w:code="14"/>
      <w:pgMar w:top="{MARGIN_TOP}" w:right="{MARGIN_RIGHT}" w:bottom="{MARGIN_BOTTOM}" w:left="{MARGIN_LEFT}" w:header="720" w:footer="720" w:gutter="0"/>
      {col_str}
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
    ''')

def add_p0_gap():
    p = parse_xml(f'''
    <w:p {nsdecls("w")}>
      <w:pPr>
        <w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>
        <w:rPr>
          <w:sz w:val="2"/>
          <w:szCs w:val="2"/>
        </w:rPr>
        <w:sectPr>
          <w:type w:val="continuous"/>
          <w:pgSz w:w="{F4_W}" w:h="{F4_H}" w:code="14"/>
          <w:pgMar w:top="{MARGIN_TOP}" w:right="{MARGIN_RIGHT}" w:bottom="{MARGIN_BOTTOM}" w:left="{MARGIN_LEFT}" w:header="720" w:footer="720" w:gutter="0"/>
          <w:cols w:space="720"/>
          <w:docGrid w:linePitch="360"/>
        </w:sectPr>
      </w:pPr>
    </w:p>
    ''')
    body.append(p)

def add_empty_p():
    p = parse_xml(f'''
    <w:p {nsdecls("w")}>
      <w:pPr>
        <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
      </w:pPr>
    </w:p>
    ''')
    body.append(p)

def set_font_tahoma(run, size_pt=11.0, bold=False, underline=False):
    run.font.name = "Tahoma"
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.underline = underline
    run.font.color.rgb = RGBColor(0, 0, 0)
    rPr = run._r.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rPr.append(rf)
    rf.set(qn('w:ascii'), 'Tahoma')
    rf.set(qn('w:hAnsi'), 'Tahoma')
    rf.set(qn('w:cs'), 'Tahoma')
    rf.set(qn('w:eastAsia'), 'Tahoma')
    color_el = rPr.find(qn('w:color'))
    if color_el is not None:
        for attr in [qn('w:themeColor'), qn('w:themeTint'), qn('w:themeShade')]:
            if attr in color_el.attrib:
                del color_el.attrib[attr]

def add_romawi_heading(romawi_prefix, heading_text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.65)
    pf.first_line_indent = Cm(-0.65)
    pf.space_before = Pt(4)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.0
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    pPr = p._p.get_or_add_pPr()
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = OxmlElement('w:ind')
        pPr.append(ind)
    ind.set(qn('w:left'), '369')
    ind.set(qn('w:hanging'), '369')
    
    r_rom = p.add_run(f"{romawi_prefix}.\t")
    set_font_tahoma(r_rom, size_pt=11.0, bold=True, underline=False)
    
    r_txt = p.add_run(heading_text)
    set_font_tahoma(r_txt, size_pt=11.0, bold=True, underline=True)
    return p

def sanitize_text(text):
    t = re.sub(r'\b([A-Z])\s*:', r'\1:', text)
    t = re.sub(r'\s+([\?\:\,])', r'\1', t)
    return t.rstrip()

def add_question(num_str, text_str):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.65)
    pf.first_line_indent = Cm(-0.65)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    pPr = p._p.get_or_add_pPr()
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = OxmlElement('w:ind')
        pPr.append(ind)
    ind.set(qn('w:left'), '369')
    ind.set(qn('w:hanging'), '369')
    
    clean_text = sanitize_text(text_str)
    r_num = p.add_run(f"{num_str}.\t")
    set_font_tahoma(r_num, size_pt=11.0, bold=False)
    r_text = p.add_run(clean_text)
    set_font_tahoma(r_text, size_pt=11.0, bold=False)
    return p

def add_sub_line(text_str):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.65)
    pf.first_line_indent = Cm(0.0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if len(text_str) > 30 else WD_ALIGN_PARAGRAPH.LEFT
    
    pPr = p._p.get_or_add_pPr()
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = OxmlElement('w:ind')
        pPr.append(ind)
    ind.set(qn('w:left'), '369')
    if qn('w:hanging') in ind.attrib:
        del ind.attrib[qn('w:hanging')]
        
    clean_text = sanitize_text(text_str)
    r = p.add_run(clean_text)
    set_font_tahoma(r, size_pt=11.0, bold=False)
    return p

def add_options_inline(lbl_a, txt_a, lbl_c, txt_c, lbl_b, txt_b, lbl_d, txt_d):
    for lbl1, txt1, lbl2, txt2 in [(lbl_a, txt_a, lbl_c, txt_c), (lbl_b, txt_b, lbl_d, txt_d)]:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Cm(1.30)
        pf.first_line_indent = Cm(-0.65)
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing = 1.0
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

        pPr = p._p.get_or_add_pPr()
        tabs = OxmlElement('w:tabs')
        t_mid = OxmlElement('w:tab')
        t_mid.set(qn('w:val'), 'left')
        t_mid.set(qn('w:pos'), '2721') # 4.80 cm
        tabs.append(t_mid)
        pPr.append(tabs)

        ind = pPr.find(qn('w:ind'))
        if ind is None:
            ind = OxmlElement('w:ind')
            pPr.append(ind)
        ind.set(qn('w:left'), '737')
        ind.set(qn('w:hanging'), '369')

        clean1 = sanitize_text(txt1)
        clean2 = sanitize_text(txt2)
        line_str = f"{lbl1}\t{clean1}\t{lbl2} {clean2}"
        r = p.add_run(line_str)
        set_font_tahoma(r, size_pt=11.0, bold=False)

def add_option_single(lbl, txt):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(1.30)
    pf.first_line_indent = Cm(-0.65)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    pPr = p._p.get_or_add_pPr()
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = OxmlElement('w:ind')
        pPr.append(ind)
    ind.set(qn('w:left'), '737')
    ind.set(qn('w:hanging'), '369')

    clean = sanitize_text(txt)
    line_str = f"{lbl}\t{clean}"
    r = p.add_run(line_str)
    set_font_tahoma(r, size_pt=11.0, bold=False)

def add_image_para(src_para_idx, target_width_cm, target_height_cm):
    """
    Menyalin gambar asli dan memposisikannya sejajar dengan margin paragraf:
    Left 0.65 cm, First line 0.0 cm (Hanging 0.0 cm), Alignment Left.
    """
    p_src = src_doc.paragraphs[src_para_idx]
    p_dst = doc.add_paragraph()
    pf = p_dst.paragraph_format
    pf.left_indent = Cm(0.65)
    pf.first_line_indent = Cm(0.0)
    pf.space_before = Pt(2)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.0
    p_dst.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    pPr = p_dst._p.get_or_add_pPr()
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = OxmlElement('w:ind')
        pPr.append(ind)
    ind.set(qn('w:left'), '369')
    if qn('w:hanging') in ind.attrib:
        del ind.attrib[qn('w:hanging')]

    for child in p_src._p:
        if child.tag == qn('w:pPr'):
            continue
        cloned = copy.deepcopy(child)
        for node in cloned.iter():
            for attr in (qn('r:embed'), qn('r:link'), qn('r:id')):
                rid = node.get(attr)
                if not rid: continue
                rel = src_doc.part.rels.get(rid)
                if rel and 'image' in rel.reltype:
                    new_rid, _ = doc.part.get_or_add_image(io.BytesIO(rel.target_part.blob))
                    node.set(attr, new_rid)
                    
            if node.tag == qn('wp:extent'):
                node.set('cx', str(int(target_width_cm * 360000)))
                node.set('cy', str(int(target_height_cm * 360000)))
        p_dst._p.append(cloned)
    return p_dst

# 1. Kop ditutup P0 gap 1pt
add_p0_gap()

# 2. Seluruh badan naskah mengalir dalam 2 KOLOM seimbang!
add_romawi_heading("I", "Pilihan Ganda CP 1 (100%)")

# Q1 to Q8
pg_data_1_8 = [
    ("1", "The followings are nationalities.", [("a.", "Chinese and Japan"), ("b.", "Canada and France"), ("c.", "Singaporean and Korean"), ("d.", "Australian and America")]),
    ("2", "The followings are countries.", [("a.", "Australia and America"), ("b.", "France and Chinese"), ("c.", "Japan and Vietnamese"), ("d.", "Spain and Canadian")]),
    ("3", "The followings are subjects at school.", [("a.", "History and Assembly"), ("b.", "Art and Science"), ("c.", "Office and Geography"), ("d.", "Volleyball and PE")]),
    ("4", "The followings are stationeries.", [("a.", "Ruler and shoes"), ("b.", "Pencil sharpener and eraser"), ("c.", "Uniform and tie"), ("d.", "Pencil and desk")]),
    ("5", "The followings are animals.", [("a.", "Riding and giraffe"), ("b.", "Butterfly and strawberry"), ("c.", "Dolphin and crocodile"), ("d.", "Tennis and banana")]),
    ("6", "The followings are sports.", [("a.", "Baseball and I.t."), ("b.", "Volleyball and swimming"), ("c.", "Train and soccer"), ("d.", "Bus and bicycle")]),
    ("7", "The followings are jobs.", [("a.", "Doctor and pilot"), ("b.", "Shop assistant and hospital"), ("c.", "Teacher and riding"), ("d.", "TV station and reporter")]),
    ("8", "The followings are places of work.", [("a.", "Hospital and driver."), ("b.", "TV station and airplane"), ("c.", "Airport and school"), ("d.", "Police station and interview")]),
]

for num_s, q_txt, opts in pg_data_1_8:
    add_question(num_s, q_txt)
    # Long text questions in single column so they never wrap awkwardly
    if num_s in ('1', '2', '3', '7', '8'):
        for lbl, txt in opts:
            add_option_single(lbl, txt)
    else:
        add_options_inline(opts[0][0], opts[0][1], opts[2][0], opts[2][1],
                           opts[1][0], opts[1][1], opts[3][0], opts[3][1])

# Reading 1: Springfield Primary School (width 5.0 cm, height 7.5 cm)
add_sub_line("Read the text below and choose the correct answer for question No. 9 to 13")
add_image_para(49, target_width_cm=5.0, target_height_cm=7.5)

pg_data_9_13 = [
    ("9", "How many students are there in Springfield Primary School?", [("a.", "About 400 students"), ("b.", "About 600 students"), ("c.", "About 800 students"), ("d.", "About 1,000 students")]),
    ("10", "How many students are there in each class?", [("a.", "About 12 students"), ("b.", "About 20 students"), ("c.", "About 24 students"), ("d.", "About 30 students")]),
    ("11", "Which room is NOT mentioned in the text?", [("a.", "A Science lab"), ("b.", "A Music room"), ("c.", "A Gym"), ("d.", "An Art room")]),
    ("12", "How many computers are there in the Computer room?", [("a.", "12 computers"), ("b.", "20 computers"), ("c.", "24 computers"), ("d.", "30 computers")]),
    ("13", "How do the students feel about their school?", [("a.", "They are bored."), ("b.", "They are happy."), ("c.", "They are worried."), ("d.", "They are tired.")]),
]

for num_s, q_txt, opts in pg_data_9_13:
    add_question(num_s, q_txt)
    add_options_inline(opts[0][0], opts[0][1], opts[2][0], opts[2][1],
                       opts[1][0], opts[1][1], opts[3][0], opts[3][1])

# Reading 2: Amanda Torres (width 4.5 cm, height 8.0 cm)
add_sub_line("Read the article below then choose the correct answer for questions below it.")
add_image_para(56, target_width_cm=4.5, target_height_cm=8.0)

pg_data_14_18 = [
    ("14", "Where is Amanda Torres from?", [("a.", "Barcelona"), ("b.", "Madrid"), ("c.", "Tokyo"), ("d.", "London")]),
    ("15", "How many languages can Amanda speak?", [("a.", "Two"), ("b.", "Three"), ("c.", "Four"), ("d.", "Five")]),
    ("16", "How does Amanda go to work?", [("a.", "By car"), ("b.", "By train"), ("c.", "By taxi"), ("d.", "By bus")]),
    ("17", "Who does Amanda sometimes interview?", [("a.", "Teachers and doctors"), ("b.", "Football players and police officers"), ("c.", "Students and musicians"), ("d.", "Scientists and engineers")]),
    ("18", "What does Amanda like doing after work?", [("a.", "Reading books and cooking"), ("b.", "Playing football and swimming"), ("c.", "Listening to music, watching television, and exercising"), ("d.", "Meeting friends and shopping")]),
]

for num_s, q_txt, opts in pg_data_14_18:
    add_question(num_s, q_txt)
    if num_s in ('17', '18'):
        for lbl, txt in opts:
            add_option_single(lbl, txt)
    else:
        add_options_inline(opts[0][0], opts[0][1], opts[2][0], opts[2][1],
                           opts[1][0], opts[1][1], opts[3][0], opts[3][1])

# Questions 19 to 25
pg_data_19_25 = [
    ("19", "_______ are you studying?", "~I am studying (science)", [("a.", "What time"), ("b.", "Where"), ("c.", "What subject"), ("d.", "Who")]),
    ("20", "____ are the students?", "~They are (in the classroom)", [("a.", "What time"), ("b.", "How many"), ("c.", "How old"), ("d.", "Where")]),
    ("21", "_____ apples are there in the basket?", "There are (ten) apples in the basket.", [("a.", "How many"), ("b.", "What time"), ("c.", "Where"), ("d.", "How old")]),
    ("22", "______ is Samantha?", "She is (ten years old)", [("a.", "How old"), ("b.", "How many"), ("c.", "How"), ("d.", "Who")]),
    ("23", "_____ are you talking to?", "I am talking to (Mr. Parker)", [("a.", "What"), ("b.", "Who"), ("c.", "How"), ("d.", "What subject")]),
    ("24", "_______ are the students studying now?", "They are studying (history)", [("a.", "How old"), ("b.", "How many"), ("c.", "What subject"), ("d.", "What colour")]),
    ("25", "______ are your shoes?", "They are (black)", [("a.", "How old"), ("b.", "How many"), ("c.", "What subject"), ("d.", "What colour")]),
]

for num_s, q_txt, sub_txt, opts in pg_data_19_25:
    add_question(num_s, q_txt)
    add_sub_line(sub_txt)
    add_options_inline(opts[0][0], opts[0][1], opts[2][0], opts[2][1],
                       opts[1][0], opts[1][1], opts[3][0], opts[3][1])

# Section II: Isian CP 2
add_romawi_heading("II", "Isian CP 2 (100%)")
add_sub_line("Look at the images in the table then complete the sentences with the correct words.")
# Image 3 in column: width 8.5 cm, height 7.6 cm
add_image_para(108, target_width_cm=8.5, target_height_cm=7.6)

# Section III: Isian CP 3
add_romawi_heading("III", "Isian CP 3 (100%)")
add_sub_line("Rewrite the words in order to make correct sentences.")

isian_cp3 = [
    ("1", "reading / The children / are / in the library"),
    ("2", "football / Some children / are playing / in the playground"),
    ("3", "studying / Some students / maths / are."),
    ("4", "the computer room / There are / two students / in"),
    ("5", "students / There are / twenty-five / in my class.")
]

for num_s, q_txt in isian_cp3:
    add_question(num_s, q_txt)
    add_sub_line("= ....................................................................................")

# Section IV: Essay CP 4
add_romawi_heading("IV", "Essay CP 4 (100%)")
add_sub_line("Read the text below and answer the question.")
# Image 4 in column: width 4.5 cm, height 6.8 cm
add_image_para(133, target_width_cm=4.5, target_height_cm=6.8)

add_sub_line("Questions:")

essay_cp4 = [
    ("1", "How old is Mary Clark?"),
    ("2", "What does Mary like to do?"),
    ("3", "What time does Mary usually go to bed?"),
    ("4", "What does Dr. Sara Jones tell Mary to do?"),
    ("5", "What time should Mary go to bed?")
]

for num_s, q_txt in essay_cp4:
    add_question(num_s, q_txt)

# Tail: Good Luck
p_gl = doc.add_paragraph()
pf = p_gl.paragraph_format
pf.left_indent = Cm(0.0)
pf.first_line_indent = Cm(0.0)
pf.space_before = Pt(6)
pf.space_after = Pt(0)
pf.line_spacing = 1.0
p_gl.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_gl = p_gl.add_run("Good Luck")
set_font_tahoma(r_gl, size_pt=11.0, bold=True)

# Final sectPr on body: 2 COLUMNS
body.append(make_sectPr(cols=2))

doc.save(output_path)
print("Saved 2-column balanced test doc:", output_path)
'@ | Out-File -Encoding utf8 C:\Users\yonat\AppData\Local\Temp\build_bi5_balanced.py
python C:\Users\yonat\AppData\Local\Temp\build_bi5_balanced.py
