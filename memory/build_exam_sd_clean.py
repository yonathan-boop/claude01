#!/usr/bin/env python3
"""
build_exam_sd_clean.py - Engine Standar Baku Penyuntingan Naskah Soal Ujian SD
SD Swasta Methodist-11 Medan

ATURAN PENAMAAN MUTLAK:
- Unit editing HANYA menambahkan kata 'edit'.
- DILARANG KERAS menyisipkan kata 'OK' jika nama berkas asal tidak memiliki kata 'OK'.
  Contoh:
  'Bahasa Inggris 6 Winna.docx' -> 'Bahasa Inggris 6 Winna edit.docx'
  'Agama 1 Rio OK.docx'         -> 'Agama 1 Rio OK edit.docx' (karena asal sudah ada OK)
"""

import os
import sys
import copy
import re
import docx
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

F4_W = 12242
F4_H = 18722
MARGIN_TOP = 284     # 0.50 cm
MARGIN_BOTTOM = 340  # 0.60 cm
MARGIN_LEFT = 567    # 1.00 cm
MARGIN_RIGHT = 567   # 1.00 cm
COL_SPACING = 567    # 1.00 cm

def generate_output_filename(input_filename):
    """
    Aturan Mutlak Penamaan:
    Hanya menambahkan kata 'edit'.
    Dilarang menambahkan 'OK' jika dari awal tidak ada.
    """
    base, ext = os.path.splitext(input_filename)
    base_clean = base.strip()
    if base_clean.lower().endswith(" edit"):
        return f"{base_clean}{ext}"
    return f"{base_clean} edit{ext}"

def make_sectPr(cols=1, continuous=True):
    col_str = f'<w:cols {nsdecls("w")} w:num="{cols}" w:space="{COL_SPACING}"/>' if cols > 1 else f'<w:cols {nsdecls("w")} w:space="720"/>'
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

if __name__ == '__main__':
    # Test nama file
    assert generate_output_filename("Bahasa Inggris 6 Winna.docx") == "Bahasa Inggris 6 Winna edit.docx"
    assert generate_output_filename("Agama 1 Rio OK.docx") == "Agama 1 Rio OK edit.docx"
    print("Test penamaan lolos 100% tanpa menyisipkan kata OK palsu.")
