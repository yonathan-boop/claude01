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

master_path = r"\\192.168.195.7\Methodist-11 Document\SOAL UJIAN\Soal Ujian Semester I T.P.2026-2027\SD SWASTA METHODIST.docx"
src_p = r"\\192.168.195.7\Methodist-11 Document\SOAL UJIAN\Soal Ujian Semester I T.P.2026-2027\Bahasa Inggris\Bahasa Inggris 5 Linda.docx"

out_dir = r"C:\Users\yonat\Desktop\CLAUDE\output"
os.makedirs(out_dir, exist_ok=True)
local_out = os.path.join(out_dir, "Bahasa Inggris 5 Linda edit.docx")
share_out = r"\\192.168.195.7\Methodist-11 Document\SOAL UJIAN\Soal Ujian Semester I T.P.2026-2027\Bahasa Inggris\Bahasa Inggris 5 Linda edit.docx"

doc = docx.Document(master_path)
src_doc = docx.Document(src_p)

# 1. KOP SURAT RESMI (VA SD, B. Inggris, Kamis, 3 Desember 2026, Nilai 70)
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

def make_sectPr():
    return parse_xml(f'''
    <w:sectPr {nsdecls("w")}>
      <w:type w:val="continuous"/>
      <w:pgSz w:w="{F4_W}" w:h="{F4_H}" w:code="14"/>
      <w:pgMar w:top="{MARGIN_TOP}" w:right="{MARGIN_RIGHT}" w:bottom="{MARGIN_BOTTOM}" w:left="{MARGIN_LEFT}" w:header="720" w:footer="720" w:gutter="0"/>
      <w:cols w:space="720"/>
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

def add_romawi_heading(romawi_prefix, heading_text, page_break_before=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.65)
    pf.first_line_indent = Cm(-0.65)
    pf.space_before = Pt(0)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.0
    if page_break_before:
        pf.page_break_before = True
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
    pf.space_after = Pt(2)
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

def add_image_para(src_para_idx, target_width_cm, target_height_cm):
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

# Gap 1pt di bawah kop
add_p0_gap()

# ============================================================
# HALAMAN 1: ISIAN CP 2 & ISIAN CP 3
# ============================================================
add_romawi_heading("I", "Isian CP 2 (100%)")
add_sub_line("Look at the images in the table then complete the sentences with the correct words.")
# Image 3 fits Page 1 comfortably: width 11.5 cm, height 10.0 cm
add_image_para(108, target_width_cm=11.5, target_height_cm=10.0)

# PEMBATAS SEKSI ANTARA ISIAN CP 2 DAN ISIAN CP 3 (1 BARIS ENTER KOSONG)
add_empty_p()

# Section II: Isian CP 3 (100%)
add_romawi_heading("II", "Isian CP 3 (100%)")
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
    add_sub_line("= ....................................................................................................")

# ============================================================
# HALAMAN 2: ESSAY CP 4 (PINDAH KE HALAMAN 2 DENGAN PAGE_BREAK_BEFORE)
# ============================================================
add_romawi_heading("III", "Essay CP 4 (100%)", page_break_before=True)
add_sub_line("Read the text below and answer the question.")

# Gambar Surat Dear Doctor / Dear Mary (width 8.5 cm, height 12.8 cm)
add_image_para(133, target_width_cm=8.5, target_height_cm=12.8)

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
    add_sub_line("Jb : ....................................................................................................")

# Tail: Good Luck
p_gl = doc.add_paragraph()
pf = p_gl.paragraph_format
pf.left_indent = Cm(0.0)
pf.first_line_indent = Cm(0.0)
pf.space_before = Pt(14)
pf.space_after = Pt(0)
pf.line_spacing = 1.0
p_gl.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_gl = p_gl.add_run("Good Luck")
set_font_tahoma(r_gl, size_pt=11.0, bold=True)

# Final sectPr di body (1 kolom continuous)
body.append(make_sectPr())

doc.save(local_out)
print(f"[OK] Tersimpan lokal: {local_out}")

# Salin ke Network Share
import shutil
shutil.copy2(local_out, share_out)
print(f"[OK] Tersalin ke Share: {share_out}")
