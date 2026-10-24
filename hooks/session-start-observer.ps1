[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ClaudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
$HomeDir = $HOME

# Safe non-blocking stdin read
$SessionId = ""
if ([Console]::IsInputRedirected) {
    try {
        $task = [Console]::In.ReadToEndAsync()
        if ($task.Wait(1000)) {
            $payload = $task.Result
            if ($payload) {
                $jsonInput = ConvertFrom-Json $payload
                if ($jsonInput.session_id) { $SessionId = [string]$jsonInput.session_id }
            }
        }
    } catch {
        $SessionId = ""
    }
}

# 1. Read Active Tasks
$ActiveTasksPath = Join-Path $ClaudeDir "projects\C--Users-yonat\memory\active-tasks.md"
if (-not (Test-Path $ActiveTasksPath)) {
    $ActiveTasksPath = Join-Path $ClaudeDir "memory\active-tasks.md"
}

$ActiveTasksSummary = ""
if (Test-Path $ActiveTasksPath) {
    try {
        $lines = Get-Content -LiteralPath $ActiveTasksPath -Encoding UTF8
        $inFrontmatter = $false
        $taskLines = @()
        foreach ($line in $lines) {
            if ($line -eq '---') {
                $inFrontmatter = -not $inFrontmatter
                continue
            }
            if (-not $inFrontmatter -and $line.Trim()) {
                $taskLines += $line
            }
        }
        $ActiveTasksSummary = ($taskLines | Select-Object -First 15) -join "`n"
    } catch {
        $ActiveTasksSummary = "Gagal membaca active-tasks.md"
    }
} else {
    $ActiveTasksSummary = "Belum ada active-tasks.md."
}

# 2. Read Latest Observations
$LogPath = Join-Path $HomeDir "skill-observations\log.md"
$ObsSummary = ""
if (Test-Path $LogPath) {
    try {
        $obsLines = Get-Content -LiteralPath $LogPath -Encoding UTF8
        $matched = $obsLines | Where-Object { $_ -match '^(##|###|\- \*\*Trigger|\- \*\*Status)' } | Select-Object -First 10
        if ($matched) {
            $ObsSummary = $matched -join "`n"
        } else {
            $ObsSummary = "Log observasi kosong."
        }
    } catch {
        $ObsSummary = "Gagal membaca skill-observations/log.md"
    }
} else {
    $ObsSummary = "Belum ada skill-observations/log.md."
}

# 3. Construct Context Payload
$ContextText = @"
<task-observer-startup>
[TASK OBSERVER AUTO-LOADED ON SESSION START]
Konteks aktivitas terakhir dan pending tasks:

=== PEKERJAAN AKTIF TERAKHIR ===
$ActiveTasksSummary

=== OBSERVASI TERAKHIR ===
$ObsSummary

Instruksi Operasional:
1. Task Observer aktif di background sejak awal sesi.
2. Catat pattern/koreksi berulang ke 'skill-observations/log.md'.
3. Simpan update status pekerjaan ke 'memory/active-tasks.md'.
</task-observer-startup>
"@

$OutputObj = @{
    systemMessage = "TASK OBSERVER AKTIF: Catatan aktivitas terakhir dan pending tasks telah dimuat ke konteks sesi."
    hookSpecificOutput = @{
        hookEventName = "SessionStart"
        additionalContext = $ContextText
    }
}

$OutputJson = $OutputObj | ConvertTo-Json -Depth 5 -Compress
Write-Output $OutputJson
