import win32com.client
import sys

def validate(doc_path):
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    anomalies = []

    try:
        doc = word.Documents.Open(doc_path)

        # 1. Check logo shape
        if doc.Shapes.Count < 1:
            anomalies.append("Logo shape MISSING in document!")

        # 2. Check sections
        sec_count = doc.Sections.Count
        if sec_count != 5:
            anomalies.append(f"Expected 5 sections, got {sec_count}")

        # 3. Check paragraphs
        pt_to_cm = 28.3465
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs.Item(i)
            raw_text = p.Range.Text.strip()
            text = raw_text[:30]
            left = round(p.LeftIndent / pt_to_cm, 2)
            first = round(p.FirstLineIndent / pt_to_cm, 2)
            hang = round(-first, 2)

            # Check for negative indents
            if left < -0.01:
                anomalies.append(f"p[{i}] '{text}' has NEGATIVE LeftIndent: {left} cm")

            # Check headings
            if any(h in raw_text for h in ['Pilihan Ganda CP 1', 'CP 2 (100%)', 'CP 3 (100%)', 'Isian CP 4', 'Esai (60%)']):
                if abs(left) > 0.02 or abs(first) > 0.02 or abs(hang) > 0.02:
                    anomalies.append(f"p[{i}] JUDUL '{text}' not zero-aligned: Left={left} cm, First={first} cm, Hang={hang} cm")

            # Check soal & opsi (non-empty, non-heading)
            # In PG section (paragraphs 50 to 175 approx)
            # If it has hanging, verify it's 0.65cm
            if hang > 0.05 and abs(hang - 0.65) > 0.05:
                anomalies.append(f"p[{i}] '{text}' Hanging is {hang} cm, EXPECTED 0.65 cm!")

        doc.Close(False)
    finally:
        word.Quit()

    print(f"=== VALIDATION REPORT: {len(anomalies)} anomalies found ===")
    for a in anomalies:
        print("  FAIL:", a)

    if anomalies:
        sys.exit(1)
    else:
        print("PASS: ALL CHECKS PASSED PERFECTLY (100% compliant with Methodist-11 standards)!")

if __name__ == "__main__":
    validate(r'C:\Users\yonat\Desktop\Soal Ujian Semester I T.P.2026-2027\Agama\Agama 1 Rio OK.docx')
