@echo off
REM ============================================================
REM  DSH won't start after enabling Agent Teams? Run this.
REM  Restores the two profile files backed up BEFORE the
REM  Agent Teams bundle was added, then starts DSH again.
REM  No admin needed. Safe to run twice.
REM
REM  If DSH is currently running, close it first (it may write
REM  these files back on exit).
REM ============================================================
setlocal
set PROFILE=E:\Agent-bluefish\Save\dsh-home\profiles\desktop
set BACKUP=E:\Agent-bluefish\Backups\agent-team-20261119
set LAUNCHER=E:\deepseek\fish-dsh-launch.vbs

echo.
echo  This will roll back the Agent Teams change.
echo  Make sure DSH is closed. Press Ctrl+C to abort.
timeout /t 6 >nul

echo [1/3] Restoring package.json ...
if exist "%BACKUP%\package.json.before" (
  copy /Y "%BACKUP%\package.json.before" "%PROFILE%\package.json" >nul
  if errorlevel 1 (echo       FAILED) else (echo       ok)
) else (
  echo       backup missing: %BACKUP%\package.json.before
  pause
  exit /b 1
)

echo [2/3] Restoring pnpm-lock.yaml ...
if exist "%BACKUP%\pnpm-lock.yaml.before" (
  copy /Y "%BACKUP%\pnpm-lock.yaml.before" "%PROFILE%\pnpm-lock.yaml" >nul
  echo       ok
) else (
  echo       skipped
)

echo [3/3] Starting DSH through the normal launcher ...
if exist "%LAUNCHER%" (
  start "" wscript.exe "%LAUNCHER%"
  echo       ok
) else if exist "E:\deepseek\DeepSeek Harness.exe" (
  start "" "E:\deepseek\DeepSeek Harness.exe"
  echo       launcher missing, started exe directly
) else (
  echo       not found, start DSH yourself
)

echo.
echo Done. Verify: the plugins page should no longer show Agent Teams.
timeout /t 6 >nul
