import docx
from docx.shared import Cm, Inches, Pt
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# 1. Paths
kop_path = r'C:\Users\yonat\Desktop\Soal Ujian Semester I T.P.2026-2027\SD SWASTA METHODIST.docx'
backup_path = r'C:\Users\yonat\.claude\projects\C--Users-yonat\memory\backups\Agama 1 Rio OK.raw_backup.docx'
target_path = r'C:\Users\yonat\Desktop\Soal Ujian Semester I T.P.2026-2027\Agama\Agama 1 Rio OK.docx'

doc_kop = docx.Document(kop_path)
tbl_xml = doc_kop.tables[0]._tbl.xml

# We start from raw backup to guarantee a clean slate
doc = docx.Document(backup_path)

# Remove the 2 raw header paragraphs ('KELAS : 1', 'PELAJARAN : ...')
p0 = doc.paragraphs[0]._p
p1 = doc.paragraphs[1]._p
p0.getparent().remove(p0)
p1.getparent().remove(p1)

# Clean all trailing tabs and extra spaces in all paragraphs
for p in doc.paragraphs:
    # Only clean options/questions, preserve necessary structure
    t = p.text
    if '\t' in t or '  ' in t:
        cleaned = t.replace('\t', '').strip()
        # If it was non-empty, update text
        if cleaned:
            p.text = cleaned

# Insert Kop table before paragraph 0
new_tbl = parse_xml(tbl_xml)
doc.paragraphs[0]._p.addprevious(new_tbl)

# Update kop table cells
t = doc.tables[0]
for r_i, val in [(0, 'Agama'), (1, 'Selasa, 1 Desember 2026'), (2, 'IA SD')]:
    cell_p = t.cell(r_i, 4).paragraphs[0]
    cell_p.text = ''
    run = cell_p.add_run(val)
    run.font.name = 'Tahoma'
    run.font.size = Pt(7)
    run.font.bold = True

# Create Section 0 separator paragraph right after Kop table.
# CRITICAL: <w:type w:val="continuous"/> inside sectPr prevents Word from creating a page break!
sep_p_xml = f'''
<w:p {nsdecls("w")}>
  <w:pPr>
    <w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>
    <w:rPr>
      <w:sz w:val="2"/>
      <w:szCs w:val="2"/>
    </w:rPr>
    <w:sectPr>
      <w:type w:val="continuous"/>
      <w:pgSz w:w="12240" w:h="18720" w:code="14"/>
      <w:pgMar w:top="283" w:right="567" w:bottom="283" w:left="567" w:header="709" w:footer="709" w:gutter="0"/>
      <w:cols w:num="1" w:space="708"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:pPr>
</w:p>
'''
doc.paragraphs[0]._p.addprevious(parse_xml(sep_p_xml))

# doc.paragraphs[0] is now the separator
# doc.paragraphs[1] is 'Pilihan Ganda CP 1 (100%)' (Judul Pertama)
first_title = doc.paragraphs[1]
first_title.paragraph_format.space_before = Pt(0)
first_title.paragraph_format.space_after = Pt(2)

# Now find where Isian starts so we can make Pilihan Ganda 2 columns and Isian/Esai 1 column
# Find paragraph with 'Isian CP 4 (40%)'
isian_idx = None
for idx, p in enumerate(doc.paragraphs):
    if 'Isian CP 4' in p.text:
        isian_idx = idx
        break

print(f"Isian starts at paragraph {isian_idx}: {doc.paragraphs[isian_idx].text}")

# The paragraph right BEFORE isian_idx (the last PG option) will hold the Section 1 sectPr (2 columns, continuous)
last_pg_p = doc.paragraphs[isian_idx - 1]
# Add sectPr to last_pg_p.pPr
pg_sectPr_xml = f'''
<w:sectPr {nsdecls("w")}>
  <w:type w:val="continuous"/>
  <w:pgSz w:w="12240" w:h="18720" w:code="14"/>
  <w:pgMar w:top="283" w:right="567" w:bottom="283" w:left="567" w:header="709" w:footer="709" w:gutter="0"/>
  <w:cols w:num="2" w:space="708"/>
  <w:docGrid w:linePitch="360"/>
</w:sectPr>
'''
last_pg_p._p.get_or_add_pPr().append(parse_xml(pg_sectPr_xml))

# Section 2 is the document-level sectPr (for Isian & Esai): 1 column, continuous!
body_sectPr = doc.sections[-1]._sectPr
# Set 1 column
for c in body_sectPr.xpath('.//w:cols'):
    c.getparent().remove(c)
body_sectPr.append(parse_xml(f'<w:cols {nsdecls("w")} w:num="1" w:space="708"/>'))
# Set continuous
if not body_sectPr.xpath('.//w:type'):
    body_sectPr.insert(0, parse_xml(f'<w:type {nsdecls("w")} w:val="continuous"/>'))
else:
    body_sectPr.xpath('.//w:type')[0].set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'continuous')

# Ensure page size and margins on document-level section
doc.sections[-1].page_width = Inches(8.5)
doc.sections[-1].page_height = Inches(13.0)
doc.sections[-1].top_margin = Cm(0.5)
doc.sections[-1].bottom_margin = Cm(0.5)
doc.sections[-1].left_margin = Cm(1.0)
doc.sections[-1].right_margin = Cm(1.0)

# Now ensure proper blank lines / enters above headings:
# Headings: 'CP 2 (100%)', 'CP 3 (100%)', 'Isian CP 4 (40%)', 'Esai (60%)'
headings_with_enter = ['CP 2 (100%)', 'CP 3 (100%)', 'Isian CP 4 (40%)', 'Esai (60%)']

for idx, p in enumerate(list(doc.paragraphs)):
    t_text = p.text.strip()
    if any(h == t_text for h in headings_with_enter):
        # Check previous paragraph
        prev_p = doc.paragraphs[idx - 1] if idx > 0 else None
        if prev_p is not None and prev_p.text.strip() != '':
            blank_xml = f'''
            <w:p {nsdecls("w")}>
              <w:pPr>
                <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
              </w:pPr>
            </w:p>
            '''
            p._p.addprevious(parse_xml(blank_xml))

doc.save(target_path)
print("SUCCESS: Clean 3-section layout built!")
