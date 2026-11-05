import docx
import copy
import io
import os
import re
import shutil
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

master_p = r"\\192.168.195.7\Methodist-11 Document\SOAL UJIAN\Soal Ujian Semester I T.P.2026-2027\SD SWASTA METHODIST.docx"
src_p = r"\\192.168.195.7\Methodist-11 Document\SOAL UJIAN\Soal Ujian Semester I T.P.2026-2027\Bahasa Inggris\Bahasa Inggris 5 Linda.docx"

out_dir = r"C:\Users\yonat\Desktop\CLAUDE\output"
os.makedirs(out_dir, exist_ok=True)
local_out = os.path.join(out_dir, "Bahasa Inggris 5 Linda edit.docx")
share_out = r"\\192.168.195.7\Methodist-11 Document\SOAL UJIAN\Soal Ujian Semester I T.P.2026-2027\Bahasa Inggris\Bahasa Inggris 5 Linda edit.docx"

doc_m = docx.Document(master_p)
src_doc = docx.Document(src_p)
orig_doc = docx.Document(src_p)

# 1. Re-embed logo into src_doc
logo_rel = doc_m.part.rels.get('rId5')
new_logo_rid, _ = src_doc.part.get_or_add_image(io.BytesIO(logo_rel.target_part.blob))

# 2. Prepare tbl_master
tbl_master = copy.deepcopy(doc_m.tables[0]._tbl)
for t in tbl_master.xpath('.//w:tr[1]/w:tc[5]//w:t'): t.text = "B. Inggris"
for t in tbl_master.xpath('.//w:tr[2]/w:tc[5]//w:t'): t.text = "Kamis, 3 Desember 2026"
for t in tbl_master.xpath('.//w:tr[3]/w:tc[5]//w:t'): t.text = "VA SD"
for t in tbl_master.xpath('.//w:tr[4]/w:tc[5]//w:t'): t.text = " " * 17 + "/ "
for blip in tbl_master.xpath('.//a:blip'):
    blip.set(qn('r:embed'), new_logo_rid)

# 3. Geometry constants F4 & margins
F4_W = 12242
F4_H = 18722
MARGIN_TOP = 284     # 0.50 cm
MARGIN_BOTTOM = 340  # 0.60 cm
MARGIN_LEFT = 567    # 1.00 cm
MARGIN_RIGHT = 567   # 1.00 cm
COL_SPACING = 567    # 1.00 cm

def make_sectPr(cols=1, continuous=True, start_type=None):
    col_str = f'<w:cols {nsdecls("w")} w:num="{cols}" w:space="{COL_SPACING}"/>' if cols > 1 else f'<w:cols {nsdecls("w")} w:space="720"/>'
    if start_type:
        type_str = f'<w:type w:val="{start_type}"/>'
    else:
        type_str = '<w:type w:val="continuous"/>' if continuous else ''
    return parse_xml(f'''
    <w:sectPr {nsdecls("w")}>
      {type_str}
      <w:pgSz w:w="{F4_W}" w:h="{F4_H}" w:code="14"/>
      <w:pgMar w:top="{MARGIN_TOP}" w:right="{MARGIN_RIGHT}" w:bottom="{MARGIN_BOTTOM}" w:left="{MARGIN_LEFT}" w:header="720" w:footer="720" w:gutter="0"/>
      {col_str}
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
    ''')

# Insert kop table at the very top of src_doc body
body = src_doc._body._element
first_p = body.find(qn('w:p'))
first_p.addprevious(tbl_master)

# Remove old header paragraphs (indices 0 to 5)
for p in list(src_doc.paragraphs)[:6]:
    body.remove(p._p)

# Gap paragraph under Kop with 1-column sectPr (rapat 0 pt)
p0_gap = parse_xml(f'''
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
src_doc.paragraphs[0]._p.addprevious(p0_gap)

# Format P[0] (which was 'CP 1') to official Roman heading (space_before=0 untuk audit naskah):
p_cp1 = src_doc.paragraphs[0]
p_cp1.text = ""
pPr = p_cp1._p.get_or_add_pPr()
ind = OxmlElement('w:ind')
ind.set(qn('w:left'), '369')
ind.set(qn('w:hanging'), '369')
pPr.append(ind)
sp = OxmlElement('w:spacing')
sp.set(qn('w:before'), '0')
sp.set(qn('w:after'), '20')
pPr.append(sp)

r_rom = p_cp1.add_run("I.\t")
r_rom.font.name = "Tahoma"
r_rom.font.size = Pt(11.0)
r_rom.bold = True
r_txt = p_cp1.add_run("Pilihan Ganda CP 1 (100%)")
r_txt.font.name = "Tahoma"
r_txt.font.size = Pt(11.0)
r_txt.bold = True
r_txt.underline = True

# P[1] is instruction: 'Choose the correct answer.'
p_inst = src_doc.paragraphs[1]
p_inst.text = "Choose the correct answer."
p_inst.runs[0].font.name = "Tahoma"
p_inst.runs[0].font.size = Pt(11.0)
p_inst_pPr = p_inst._p.get_or_add_pPr()
ind2 = OxmlElement('w:ind')
ind2.set(qn('w:left'), '369')
p_inst_pPr.append(ind2)
sp2 = OxmlElement('w:spacing')
sp2.set(qn('w:before'), '0')
sp2.set(qn('w:after'), '40')
p_inst_pPr.append(sp2)

# End of 1-column section on p_inst (transition to 2-columns for Pilgan)
p_inst_pPr.append(make_sectPr(cols=1, continuous=True))

# Remove duplicated instruction if present in P[2]
if "Choose the correct answer" in src_doc.paragraphs[2].text:
    body.remove(src_doc.paragraphs[2]._p)

# Find CP 2
cp2_idx = None
for i, p in enumerate(src_doc.paragraphs):
    if "CP 2" in p.text and i > 5:
        cp2_idx = i
        break

print(f"CP 2 found at paragraph index {cp2_idx}")

# Set font on all Pilgan paragraphs to Tahoma 11pt (standar Methodist-11)
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

for p_i in range(2, cp2_idx):
    p_item = src_doc.paragraphs[p_i]
    for r in p_item.runs:
        is_b = r.bold
        is_u = r.underline
        set_font_tahoma(r, size_pt=11.0, bold=bool(is_b), underline=bool(is_u))

# The paragraph right before CP 2 (Question 25 options) ends the 2-column section!
p_pilgan_end = src_doc.paragraphs[cp2_idx - 1]
p_pilgan_end._p.get_or_add_pPr().append(make_sectPr(cols=2, continuous=True))

# Remove everything from CP 2 to the end of src_doc
paras_to_remove = list(src_doc.paragraphs)[cp2_idx:]
for p in paras_to_remove:
    body.remove(p._p)

# Remove any existing final sectPr
final_sect = body.find(qn('w:sectPr'))
if final_sect is not None:
    body.remove(final_sect)

def add_empty_p():
    p = parse_xml(f'''
    <w:p {nsdecls("w")}>
      <w:pPr>
        <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
      </w:pPr>
    </w:p>
    ''')
    body.append(p)

def add_romawi_heading(romawi_prefix, heading_text, page_break_before=False):
    p = src_doc.add_paragraph()
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
    p = src_doc.add_paragraph()
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
    p = src_doc.add_paragraph()
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

def add_image_para_from_orig(orig_para_idx, target_width_cm, target_height_cm):
    p_src = orig_doc.paragraphs[orig_para_idx]
    p_dst = src_doc.add_paragraph()
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
                rel = orig_doc.part.rels.get(rid)
                if rel and 'image' in rel.reltype:
                    new_rid, _ = src_doc.part.get_or_add_image(io.BytesIO(rel.target_part.blob))
                    node.set(attr, new_rid)
                    
            if node.tag == qn('wp:extent'):
                node.set('cx', str(int(target_width_cm * 360000)))
                node.set('cy', str(int(target_height_cm * 360000)))
        p_dst._p.append(cloned)
    return p_dst

# ============================================================
# HALAMAN 3: ISIAN CP 2 & ISIAN CP 3 (PAGE_BREAK_BEFORE)
# ============================================================
add_romawi_heading("II", "Isian CP 2 (100%)", page_break_before=True)
add_sub_line("Look at the images in the table then complete the sentences with the correct words.")
# Compact image 3 to 8.2 cm height so Page 3 comfortably fits all of Isian CP 2 & Isian CP 3!
add_image_para_from_orig(108, target_width_cm=9.8, target_height_cm=8.2)

# PEMBATAS SEKSI
add_empty_p()

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
    add_sub_line("= ....................................................................................................")

# ============================================================
# HALAMAN 4: ESSAY CP 4 (PAGE_BREAK_BEFORE)
# ============================================================
add_romawi_heading("IV", "Essay CP 4 (100%)", page_break_before=True)
add_sub_line("Read the text below and answer the question.")
add_image_para_from_orig(133, target_width_cm=8.5, target_height_cm=12.8)

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
p_gl = src_doc.add_paragraph()
pf = p_gl.paragraph_format
pf.left_indent = Cm(0.0)
pf.first_line_indent = Cm(0.0)
pf.space_before = Pt(14)
pf.space_after = Pt(0)
pf.line_spacing = 1.0
p_gl.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_gl = p_gl.add_run("Good Luck")
set_font_tahoma(r_gl, size_pt=11.0, bold=True)

# Final sectPr in body: 1 column continuous
body.append(make_sectPr(cols=1, continuous=True))

src_doc.save(local_out)
print(f"[OK] Tersimpan lokal: {local_out}")

# Salin ke Network Share
shutil.copy2(local_out, share_out)
print(f"[OK] Tersalin ke Share: {share_out}")
