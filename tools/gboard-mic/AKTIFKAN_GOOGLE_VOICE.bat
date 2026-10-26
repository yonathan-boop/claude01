@echo off
title Google Voice Launcher

:: Matikan proses lama jika ada
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name LIKE 'python%%' AND CommandLine LIKE '%%gboard_mic%%'\" | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1

:: Jalankan gboard_mic di background tanpa jendela hitam
start "" wscript.exe "%~dp0Gboard_Mic.vbs"

exit
