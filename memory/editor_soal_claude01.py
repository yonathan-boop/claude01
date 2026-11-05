#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
editor_soal_claude01.py - Engine Standar Baku Editing Naskah Soal Ujian SD (Claude 01)
SD Swasta Methodist-11 Medan

VERSI: 00.1
IDENTITAS MESIN: Claude 01 (Node 01)

ATURAN BAKU RESMI (KUMULATIF & TERUJI FISIK):
1. KOP MASTER NATIVE & PRESERVASI:
   - Template resmi: 'SD SWASTA METHODIST.docx'.
   - Pengisian via Pure Paste Value pada simpul XML <w:t> (tanpa merusak <w:pPr>).
   - Sinkronisasi Mapel & Hari/Tgl: Mengikuti mutlak Tabel 1 Jadwal SD di dokumen master:
     * 'B. Inggris'         -> Kamis, 3 Desember 2026
     * 'B. Indonesia'       -> Jumat, 4 Desember 2026
     * 'E. Mathematics'     -> Sabtu, 5 Desember 2026 (atau Selasa, 1 Des Kls 1-2)
     * 'Matematika'         -> Kamis, 3 Desember 2026
     * 'Pendidikan Pancasila' -> Rabu, 2 Desember 2026
     * 'IPAS' (1-2) / 'IPA' (3-6) -> Rabu, 2 Desember 2026
     * 'IPS'                -> Selasa, 1 Desember 2026 (Sabtu, 5 Des Kls 3-6)
     * 'Bahasa Mandarin'    -> Senin, 30 November 2026
     * 'Seni Musik'         -> Senin, 30 November 2026
     * 'Agama'              -> Selasa, 1 Desember 2026
     * 'Seni Rupa' / 'KTK'  -> Sabtu, 5 Desember 2026
   - Preservasi NIS/Nama: Tepat 17 spasi sengaja sebelum garis miring ('                 / ').
   - Logo sekolah fisik: media/image1.png rId5 utuh di Cell(0,0), kotak Nilai utuh.

2. PENAMAAN BERKAS (ANTI-LABEL OK LIAR):
   - Hak unit editing HANYA menambahkan kata 'edit' ([Nama Asli] edit.docx).
   - DILARANG menambahkan 'OK' jika draf asal guru tidak ada 'OK'.
   - Contoh: 'Bahasa Inggris 6 Winna.docx' -> 'Bahasa Inggris 6 Winna edit.docx'.
   - Pengecualian: Hanya jika asal dari guru memang sudah ada 'OK' ('Agama 1 Rio OK.docx' -> 'Agama 1 Rio OK edit.docx').

3. FORMAT PILIHAN GANDA MENYAMPING (2x2):
   - Opsi Kiri (a & b): 'a.\tText' dan 'b.\tText' (hanging indent Word 1.30 cm / 737 twips).
   - Lompat ke kolom kanan: Tepat 1 karakter tab '\\t' (posisi tab stop 2835 twips / 5.00 cm).
   - Opsi Kanan (c & d): 'c. Text' dan 'd. Text' (SPASI TUNGGAL SETELAH TITIK, TANPA TAB!).
   - Menjamin jarak c./d. ke teks rapat, tidak melompat renggang.
   - Opsi 1 kolom (panjang): 'a.\tText' tanpa elemen <w:tabs> agar kebal dari temuan tab liar.

4. FORMAT JUDUL SEKSI ROMAWI (I., II., III.):
   - Nomor Romawi: BOLD, NON-UNDERLINE (I.\t, II.\t, III.\t).
   - Teks Judul: BOLD, UNDERLINE (Pilihan Ganda CP 1 (100%)).
   - Indentasi Judul: Left 0.65 cm, Hanging 0.65 cm (369 twips).
   - Paragraf transisi di bawah Kop (P0 Gap Fix): 1 pt exact untuk merapatkan judul pertama ke garis kop.
   - Jeda 1 baris enter kosong di atas Judul II dan III.

5. KEBERSIHAN TEKS & TANDA BACA:
   - Dialog tanpa spasi sebelum titik dua ('A:', 'B:' bukan 'A :', 'B :').
   - Bebas trailing whitespace di akhir kalimat.
   - Tabel soal (kotak pilihan kata & teks bacaan surat) dipelihara utuh dengan border box standar.

6. HUKUM TINGKAT 1 OFFICE:
   - DILARANG KERAS memanggil word.Quit() agar tidak menutup dokumen Word yang sedang aktif diedit pengguna.
"""

import os
import sys
import copy
import re
import argparse
import docx

from docx.shared import Cm, Pt, RGBColor
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

VERSION = "00.1"

# Geometri Kertas F4 & Margin Baku SD Swasta Methodist-11
F4_W = 12242         # 21.59 cm
F4_H = 18722         # 33.02 cm
MARGIN_TOP = 284     # 0.50 cm
MARGIN_BOTTOM = 340  # 0.60 cm
MARGIN_LEFT = 567    # 1.00 cm
MARGIN_RIGHT = 567   # 1.00 cm
COL_SPACING = 567    # 1.00 cm jarak antar kolom

JADWAL_UAS1_SD_2026 = {
    'inggris': ('B. Inggris', 'Kamis, 3 Desember 2026'),
    'english': ('B. Inggris', 'Kamis, 3 Desember 2026'),
    'indonesia': ('B. Indonesia', 'Jumat, 4 Desember 2026'),
    'b.indo': ('B. Indonesia', 'Jumat, 4 Desember 2026'),
    'matematika': ('Matematika', 'Kamis, 3 Desember 2026'),
    'math': ('Matematika', 'Kamis, 3 Desember 2026'),
    'english math': ('E. Mathematics', 'Sabtu, 5 Desember 2026'),
    'e. math': ('E. Mathematics', 'Sabtu, 5 Desember 2026'),
    'mandarin': ('Bahasa Mandarin', 'Senin, 30 November 2026'),
    'musik': ('Seni Musik', 'Senin, 30 November 2026'),
    'agama': ('Agama', 'Selasa, 1 Desember 2026'),
    'pancasila': ('Pendidikan Pancasila', 'Rabu, 2 Desember 2026'),
    'pkn': ('Pendidikan Pancasila', 'Rabu, 2 Desember 2026'),
    'ipa': ('IPA', 'Rabu, 2 Desember 2026'),
    'ipas': ('IPAS', 'Rabu, 2 Desember 2026'),
    'ips': ('IPS', 'Sabtu, 5 Desember 2026'),
    'rupa': ('Seni Rupa', 'Sabtu, 5 Desember 2026'),
    'ktk': ('KTK', 'Jumat, 4 Desember 2026'),
}

def generate_output_filename(input_path):
    """
    Aturan Penamaan Berkas:
    Hanya menambahkan kata 'edit'.
    Dilarang menambahkan kata 'OK' jika nama asal tidak memiliki 'OK'.
    """
    base_name = os.path.splitext(os.path.basename(input_path))[0].strip()
    if base_name.lower().endswith(" edit"):
        return f"{base_name}.docx"
    return f"{base_name} edit.docx"

def sanitize_text(text):
    """Membersihkan spasi liar sebelum tanda baca dan trailing whitespace."""
    t = re.sub(r'\b([A-Z])\s*:', r'\1:', text)
    t = re.sub(r'\s+([\?\:\,])', r'\1', t)
    return t.rstrip()

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

def add_p0_gap(body):
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

def add_empty_p(body):
    p = parse_xml(f'''
    <w:p {nsdecls("w")}>
      <w:pPr>
        <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
      </w:pPr>
    </w:p>
    ''')
    body.append(p)

def add_sect_break_p(body, cols=2):
    p = parse_xml(f'''
    <w:p {nsdecls("w")}>
      <w:pPr>
        <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
        <w:sectPr>
          <w:type w:val="continuous"/>
          <w:pgSz w:w="{F4_W}" w:h="{F4_H}" w:code="14"/>
          <w:pgMar w:top="{MARGIN_TOP}" w:right="{MARGIN_RIGHT}" w:bottom="{MARGIN_BOTTOM}" w:left="{MARGIN_LEFT}" w:header="720" w:footer="720" w:gutter="0"/>
          <w:cols {"w:num=\"" + str(cols) + "\" w:space=\"" + str(COL_SPACING) + "\"" if cols > 1 else "w:space=\"720\""}/>
          <w:docGrid w:linePitch="360"/>
        </w:sectPr>
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

def add_romawi_heading(doc, romawi_prefix, heading_text, with_sect_cols=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.65)
    pf.first_line_indent = Cm(-0.65)
    pf.space_before = Pt(0)
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

    if with_sect_cols is not None:
        pPr.append(make_sectPr(cols=with_sect_cols))
    return p

def add_question(doc, num_str, text_str):
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

def add_sub_line(doc, text_str):
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

def add_options_inline(doc, lbl_a, txt_a, lbl_c, txt_c, lbl_b, txt_b, lbl_d, txt_d):
    """
    Opsi 2x2 menyamping:
    - Opsi kiri (a, b): 'a.\tText' (hanging indent 1.30 cm).
    - Lompat kolom: Tepat 1 elemen <w:tab> di tengah (pos 2835 / 5.00 cm).
    - Opsi kanan (c, d): 'c. Text' (SPASI SETELAH TITIK, TANPA TAB!).
    """
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
        t_mid.set(qn('w:pos'), '2835')
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

def add_option_single(doc, lbl, txt):
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

def resolve_kop_metadata(filename, folder_name=""):
    combined = f"{filename} {folder_name}".lower()
    m_cls = re.search(r'\b(?:kelas|kls)[\s_\-]*([1-6])([a-dA-D]?)\b', combined)
    if not m_cls:
        m_cls = re.search(r'\b([1-6])[\s_\-]*(?:sd|kls|kelas)\b', combined)
    grade = int(m_cls.group(1)) if m_cls else 6
    # Mandat Baku: Nama kelas wajib berakhiran sub-kelas 'A' secara default (misal VIA SD, VA SD)
    sub = m_cls.group(2).upper() if m_cls and m_cls.lastindex >= 2 and m_cls.group(2) else "A"
    roman_map = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI'}
    kelas_str = f"{roman_map.get(grade, str(grade))}{sub} SD"

    mapel = 'Mata Pelajaran'
    hari_tgl = 'Kamis, 3 Desember 2026'

    for key, (m_val, d_val) in JADWAL_UAS1_SD_2026.items():
        if key in combined:
            mapel = m_val
            hari_tgl = d_val
            break

    return kelas_str, mapel, hari_tgl, grade

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f"Engine Editor Soal Ujian Claude 01 v{VERSION}")
    parser.add_argument("input", help="Path file naskah mentah (.docx)")
    parser.add_argument("-o", "--output", help="Path file output (.docx)", default=None)
    parser.add_argument("--tpl", help="Path master SD SWASTA METHODIST.docx", default=None)
    args = parser.parse_args()

    inp = os.path.abspath(args.input)
    out = args.output or os.path.join(os.path.dirname(inp), generate_output_filename(inp))
    print(f"[*] Engine Claude 01 v{VERSION} aktif.")
    print(f"    Input  : {inp}")
    print(f"    Output : {out}")
