@echo off
REM ============================================================
REM  Restore the patched splash.js (dual mascots: left group,
REM  right Mao) after an npm/pnpm reinstall overwrote it.
REM  Pure ASCII on purpose. No admin needed.
REM ============================================================
setlocal
set SRC=E:\Agent-bluefish\Backups\startup-secret-lib-20261118\splash.js.patched
set DST=E:\Agent-bluefish\Save\dsh-home\profiles\desktop\node_modules\dsh-startup-secret\lib\splash.js

echo.
if not exist "%SRC%" (
  echo   Snapshot missing: %SRC%
  pause
  exit /b 1
)
if not exist "%DST%" (
  echo   Target missing: %DST%
  echo   The plugin may be uninstalled.
  pause
  exit /b 1
)

copy /Y "%SRC%" "%DST%" >nul
if errorlevel 1 (
  echo   Copy FAILED
) else (
  echo   Restored. Restart DSH to see it.
)
timeout /t 5 >nul
