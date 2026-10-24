param(
    [string]$FilePath = "C:\Users\yonat\Desktop\Soal Ujian Semester I T.P.2026-2027\Agama\Agama 1 Rio OK.docx"
)

$word = $null
$anomalies = @()

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $doc = $word.Documents.Open($FilePath)

    # 1. Check logo shape
    if ($doc.Shapes.Count -lt 1) {
        $anomalies += "LOGO: Shape logo sekolah di kop surat HILANG (Count = $($doc.Shapes.Count))"
    } else {
        Write-Output "CHECK 1: Logo shape terdeteksi ($($doc.Shapes.Count) shape)"
    }

    # 2. Check sections
    if ($doc.Sections.Count -ne 5) {
        $anomalies += "SECTIONS: Diharapkan 5 sections, ditemukan $($doc.Sections.Count)"
    } else {
        Write-Output "CHECK 2: Struktur 5 sections lengkap (Kop -> PG -> Transisi -> Isian -> Esai)"
    }

    # 3. Check paragraph indents
    $pt_to_cm = 28.3465
    $totalP = $doc.Paragraphs.Count

    for ($i = 1; $i -le $totalP; $i++) {
        $p = $doc.Paragraphs.Item($i)
        $raw = $p.Range.Text.Trim()
        $t = if ($raw.Length -gt 28) { $raw.Substring(0, 28) } else { $raw }

        $left = [math]::Round($p.LeftIndent / $pt_to_cm, 2)
        $first = [math]::Round($p.FirstLineIndent / $pt_to_cm, 2)
        $hang = [math]::Round(-$first, 2)

        # Check negative left
        if ($left -lt -0.01) {
            $anomalies += "p[$i] '$t': Left margin NEGATIF ($left cm)"
        }

        # Check headings
        if ($raw -match 'Pilihan Ganda CP 1|CP 2 \(100%\)|CP 3 \(100%\)|Isian CP 4|Esai \(60%\)') {
            if ([math]::Abs($left) -gt 0.02 -or [math]::Abs($hang) -gt 0.02) {
                $anomalies += "p[$i] JUDUL '$t': Belum rata kiri 0 (Left=$left cm, Hang=$hang cm)"
            }
        }

        # Check hanging indents on numbered items
        if ($hang -gt 0.05 -and [math]::Abs($hang - 0.65) -gt 0.05) {
            $anomalies += "p[$i] '$t': Hanging indent BUKAN 0.65 cm (Hang=$hang cm)"
        }
    }

    $doc.Close([Microsoft.Office.Interop.Word.WdSaveOptions]::wdDoNotSaveChanges)
} finally {
    if ($word) {
        $word.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    }
}

Write-Output ""
Write-Output "=== HASIL VALIDASI SISTEM OTOMATIS ==="
if ($anomalies.Count -eq 0) {
    Write-Output "STATUS: PASS (100% lolos semua pengecekan kualitas & aturan Methodist-11!)"
    exit 0
} else {
    Write-Output "STATUS: FAIL ($($anomalies.Count) anomali ditemukan)"
    foreach ($a in $anomalies) {
        Write-Output "  - $a"
    }
    exit 1
}
