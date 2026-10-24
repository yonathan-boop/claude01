# sync.ps1 - Sinkronisasi konfigurasi dan data Claude ke GitHub
param (
    [string]$Message = "Update data Claude: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

$ClaudeDir = $PSScriptRoot
Set-Location -Path $ClaudeDir

# 1. Sync memory terbaru dari projects ke folder memory/
$MemorySrc = Join-Path $ClaudeDir "projects\C--Users-yonat\memory"
$MemoryDst = Join-Path $ClaudeDir "memory"
if (Test-Path $MemorySrc) {
    Copy-Item -Path "$MemorySrc\*" -Destination $MemoryDst -Force
    Write-Host "[OK] Memory synced." -ForegroundColor Green
}

# 2. Sync CLAUDE.md
$HomeClaude = "$HOME\.claude"
if (Test-Path "$HomeClaude\CLAUDE.md") {
    Copy-Item -Path "$HomeClaude\CLAUDE.md" -Destination "$ClaudeDir\CLAUDE.md" -Force
}

# 3. Git status check & push ke claude01
git add -A
$Changes = git status --porcelain
if ($Changes) {
    git commit -m $Message
    git push origin main
    Write-Host "[OK] Berhasil push update ke GitHub." -ForegroundColor Green
} else {
    Write-Host "[INFO] Tidak ada perubahan untuk di-commit." -ForegroundColor Cyan
}
