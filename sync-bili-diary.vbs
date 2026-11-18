Set sh = CreateObject("WScript.Shell")
sh.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""E:\Agent-bluefish\working\sync-bili-diary.ps1""", 0, False
