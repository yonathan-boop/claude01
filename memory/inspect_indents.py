import docx

doc = docx.Document(r'C:\Users\yonat\Desktop\Soal Ujian Semester I T.P.2026-2027\Agama\Agama 1 Rio OK.docx')

print("=== CHECKING NUMBERING XML INDENTS ===")
num_part = doc.part.numbering_part
for num in num_part._element.xpath('.//*[local-name()="num"]'):
    numId = num.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numId')
    absId_elem = num.xpath('.//*[local-name()="abstractNumId"]')
    if not absId_elem: continue
    absId = absId_elem[0].get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
    absNums = num_part._element.xpath(f'.//*[local-name()="abstractNum" and @*[local-name()="abstractNumId" and .="{absId}"]]')
    if absNums:
        for lvl in absNums[0].xpath('.//*[local-name()="lvl"]'):
            ilvl = lvl.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl')
            ind = lvl.xpath('.//*[local-name()="ind"]')
            if ind:
                attrs = {k.split('}')[-1]: v for k, v in ind[0].attrib.items()}
                print(f"numId={numId} (abs={absId}) ilvl={ilvl}: {attrs}")
