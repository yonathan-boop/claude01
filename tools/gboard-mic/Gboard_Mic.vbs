Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\yonat"
WshShell.Run """C:\Users\yonat\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe"" run C:\Users\yonat\gboard_mic.py", 0, False
