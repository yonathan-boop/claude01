# -*- coding: utf-8 -*-
"""
validasi_geometri_naskah.py
Validator otomatis komprehensif naskah ujian SD/SMP Methodist-11.
Memeriksa secara ketat:
1. Geometri & Indentasi: Left indent (369 twips / 737 twips), hanging indent (369 twips).
2. Eliminasi Tab Liar: Paragraf tanpa karakter '\t' dilarang keras memiliki elemen <w:tabs>.
3. Opsi Menyamping 2x2: Wajib memiliki tepat 1 elemen <w:tab> dengan posisi presisi.
4. Keseragaman Font: Seluruh run dan penomoran otomatis (pPr/rPr) wajib seragam dengan font dominan dokumen.
5. Kemurnian Warna: Wajib hitam pekat (val="000000", tanpa themeTint/themeShade kusam).
6. Format Judul Romawi: Wajib menggunakan literal '\t' setelah angka romawi (I., II., III.), bold, teks judul bergaris bawah sedangkan nomor romawi TIDAK digarisbawahi, tanpa w:numPr.
7. Kebersihan Teks: Bebas spasi di akhir baris (trailing spaces) dan spasi sebelum tanda baca.
"""

import sys, os, glob, re, collections
import docx
from docx.oxml.ns import qn

OPTION_RE = re.compile(r'^(.*?)(?:[\t ]+)\b([c-d])\s*[\.\)]\s*(.*)$')

def validate_file(path):
    doc = docx.Document(path)
    errs = []
    
    font_counter = collections.Counter()
    for p in doc.paragraphs:
        for r in p.runs:
            name = r.font.name or (r._r.find(qn('w:rPr')) is not None and r._r.find(qn('w:rPr')).find(qn('w:rFonts')) is not None and r._r.find(qn('w:rPr')).find(qn('w:rFonts')).get(qn('w:ascii')))
            if name and r.text.strip():
                font_counter[name] += len(r.text.strip())
    dom_font = font_counter.most_common(1)[0][0] if font_counter else 'Tahoma'
    
    for i, p in enumerate(doc.paragraphs):
        t = p.text
        t_strip = t.strip()
        if not t_strip:
            continue
            
        pPr = p._p.find(qn('w:pPr'))
        if pPr is None:
            continue
            
        numPr = pPr.find(qn('w:numPr'))
        tabs = pPr.find(qn('w:tabs'))
        ind = pPr.find(qn('w:ind'))
        
        # A. Cek Judul Bagian Romawi
        if t_strip.startswith(('I.', 'II.', 'III.', 'IV.', 'V.')):
            if not re.match(r'^[I|V|X]+\.\t', t_strip):
                errs.append(f'P{i} JUDUL: Angka romawi tidak diikuti tab literal (\\t): {repr(t_strip[:30])}')
            if numPr is not None:
                errs.append(f'P{i} JUDUL: Judul memakai w:numPr (harus teks manual terformat)')
            for r in p.runs:
                if not r.bold:
                    errs.append(f'P{i} JUDUL: Run judul tidak bold: {repr(r.text[:20])}')
                # Standar Methodist-11: teks judul bergaris bawah, nomor romawi TIDAK bergaris bawah
                if re.match(r'^[I|V|X]+\.\t?$', r.text.strip()):
                    if r.underline:
                        errs.append(f'P{i} JUDUL: Nomor romawi judul dilarang bergaris bawah: {repr(r.text[:20])}')
                elif r.text.strip():
                    if not r.underline:
                        errs.append(f'P{i} JUDUL: Teks judul wajib bergaris bawah: {repr(r.text[:20])}')
            # LRN-20261019-005: Judul Bagian Romawi WAJIB Left: 0.65 cm, Hanging: 0.65 cm (369 twips)
            if ind is None:
                errs.append(f'P{i} JUDUL: Tag <w:ind> hilang pada judul seksi')
            else:
                left = ind.get(qn('w:left'))
                hang = ind.get(qn('w:hanging'))
                if left not in ('368', '369', '370'):
                    errs.append(f'P{i} JUDUL: Nilai left={left} twips judul di luar standar hanging 0.65 cm (369): {repr(t_strip[:30])}')
                if hang not in ('368', '369', '370'):
                    errs.append(f'P{i} JUDUL: Nilai hanging={hang} twips judul di luar standar hanging 0.65 cm (369): {repr(t_strip[:30])}')
                    
        # B. Cek Tab Liar (Penyebab opsi melompat / masuk ke dalam)
        if '\t' not in t and tabs is not None:
            tab_list = [tb.get(qn('w:pos')) for tb in tabs.findall(qn('w:tab'))]
            errs.append(f'P{i} TAB LIAR: Paragraf tanpa \\t memiliki elemen <w:tabs> (pos={tab_list}): {repr(t_strip[:30])}')
            
        # C. Cek Opsi Menyamping 2x2 (khusus baris opsi standalone a-d, bukan 1x4 horizontal)
        is_choice_2x2 = bool(re.match(r'^[a-d][\.\)]\t', t)) and not (re.search(r'\bb[\.\)]', t) and re.search(r'\bc[\.\)]', t))
        if '\t' in t and OPTION_RE.search(t_strip) and is_choice_2x2:
            if tabs is None:
                errs.append(f'P{i} TAB HILANG: Opsi menyamping tidak memiliki elemen <w:tabs>: {repr(t_strip[:30])}')
            else:
                tab_els = tabs.findall(qn('w:tab'))
                if len(tab_els) != 1:
                    errs.append(f'P{i} TAB GANDA: Opsi menyamping memiliki {len(tab_els)} tab stop (wajib tepat 1)')
                    
        # D. Cek Nomor Terpisah / Orphan Number (hanya jika ada titik penomoran '7.' dan bukan opsi level 1)
        ilvl_el = numPr.find(qn('w:ilvl')) if numPr is not None else None
        ilvl_val = ilvl_el.get(qn('w:val')) if ilvl_el is not None else None
        if re.match(r'^\d{1,2}\.$', t_strip) and ilvl_val != '1':
            errs.append(f'P{i} NOMOR TERPISAH: Angka nomor berdiri sendiri tanpa teks soal: {repr(t_strip)}')
            
        # E. Cek Format Opsi & Spasi Manual
        if re.search(r'^\s{2,}[a-d][\.\)]', t):
            errs.append(f'P{i} OPSI SPASI MANUAL: Opsi diawali spasi manual (harus indentasi Word): {repr(t[:20])}')
        if re.search(r'^[a-d][\.\)]\s+\t', t):
            errs.append(f'P{i} OPSI TAB KOTOR: Terdapat spasi sebelum tab pada opsi: {repr(t[:20])}')
            
        # F. Cek Indentasi Grid (369 / 737 twips) baik numPr maupun manual
        is_question = bool(numPr is not None or re.match(r'^\d{1,2}[\.\)]\t', t))
        is_choice = bool((numPr is not None and not is_question) or re.match(r'^[a-d][\.\)]\t', t))
        
        if is_question or is_choice:
            if ind is None:
                errs.append(f'P{i} GEOMETRI: Tag <w:ind> hilang pada butir soal/opsi: {repr(t_strip[:30])}')
            else:
                left = ind.get(qn('w:left'))
                hang = ind.get(qn('w:hanging'))
                expected_left = ('368', '369', '370') if is_question else ('736', '737', '738')
                # Exemption for questions with adjacent images (multiples of 369 twips: 2214, 2583)
                if left not in ('368', '369', '370', '736', '737', '738', '2214', '2583'):
                    errs.append(f'P{i} GEOMETRI: Nilai left={left} twips di luar standar (369/737): {repr(t_strip[:30])}')
                if hang not in ('368', '369', '370', '1845', '2214'):
                    errs.append(f'P{i} GEOMETRI: Nilai hanging={hang} twips di luar standar (369): {repr(t_strip[:30])}')
                    
        # E. Cek Keseragaman Font & Bullet Font
        rPr_p = pPr.find(qn('w:rPr'))
        if rPr_p is not None:
            rf_p = rPr_p.find(qn('w:rFonts'))
            if rf_p is not None and rf_p.get(qn('w:ascii')) != dom_font:
                errs.append(f'P{i} FONT BULLET: Font penomoran ({rf_p.get(qn("w:ascii"))}) beda dari dominan ({dom_font})')
                
        for j, r in enumerate(p.runs):
            rf = r.font.name or (r._r.find(qn('w:rPr')) is not None and r._r.find(qn('w:rPr')).find(qn('w:rFonts')) is not None and r._r.find(qn('w:rPr')).find(qn('w:rFonts')).get(qn('w:ascii')))
            if rf and rf != dom_font:
                errs.append(f'P{i} r{j} FONT BELANG: {rf} != {dom_font} pada teks {repr(r.text[:20])}')
                
            # F. Cek Warna Hitam Pekat
            rPr_r = r._r.find(qn('w:rPr'))
            if rPr_r is not None:
                c = rPr_r.find(qn('w:color'))
                if c is not None:
                    val = c.get(qn('w:val'))
                    tint = c.get(qn('w:themeTint'))
                    shade = c.get(qn('w:themeShade'))
                    if val in ('404040', '595959', '7f7f7f', '808080') or tint or shade:
                        errs.append(f'P{i} r{j} WARNA KUSAM: val={val}, tint={tint}, shade={shade} pada {repr(r.text[:20])}')
                        
        # G. Cek Kebersihan Teks
        if re.search(r'[ \t]+$', t):
            errs.append(f'P{i} SPASI: Terdapat trailing whitespace di akhir paragraf: {repr(t[-10:])}')
        if re.search(r' ([\?\:\,])', t):
            errs.append(f'P{i} TANDA BACA: Terdapat spasi sebelum tanda baca: {repr(t_strip[:40])}')
            
    return errs, dom_font

def main():
    paths = sys.argv[1:] if len(sys.argv) > 1 else glob.glob('*.docx')
    total_err = 0
    print('==============================================================================')
    print('AUDIT GEOMETRI & FORMATTING KOMPREHENSIF (SD/SMP METHODIST-11)')
    print('==============================================================================')
    for p in paths:
        if os.path.isfile(p) and not os.path.basename(p).startswith('~$'):
            errs, dom_font = validate_file(p)
            status = 'PASS (100% compliant)' if not errs else f'FAIL ({len(errs)} pelanggaran)'
            print(f'[*] {os.path.basename(p)} [Font: {dom_font}] -> {status}')
            for msg in errs[:15]:
                print('    [X]', msg)
            if len(errs) > 15:
                print(f'    ... dan {len(errs) - 15} pelanggaran lainnya.')
            total_err += len(errs)
    print('==============================================================================')
    print(f'HASIL AKHIR: {"SEMPURNA (0 PELANGGARAN)" if total_err == 0 else f"GAGAL ({total_err} TOTAL PELANGGARAN)"}')
    print('==============================================================================')
    sys.exit(0 if total_err == 0 else 1)

if __name__ == '__main__':
    main()
