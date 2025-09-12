@echo off
echo NUITKA Batch File 1.5

IF "%1" == "" (
  ECHO Error: Please provide a script name as the first argument.
  EXIT /B 1
)

SETLOCAL EnableDelayedExpansion
SET companyName=%2
IF "%companyName%" == "" (
  SET "companyName=EVO Smart Life"
)
echo %companyName%

SET FileVersion=%3
IF "%FileVersion%" == "" (
  SET FileVersion=1.0.0.0
)
echo %FileVersion%

SET FileDescription="Part of EVO tool set"

python -m nuitka ^
  --onefile ^
  --standalone ^
  --windows-icon-from-ico=evo-48.png ^
  --windows-console-mode=disable ^
  --company-name="%companyName%" ^
  --copyright="%companyName%" ^
  --file-version=%FileVersion% ^
  --file-description=%FileDescription% ^
  --include-module=PIL.Image ^
  --include-module=PIL.ImageQt ^
  --include-module=PIL.ImageDraw ^
  --include-module=PIL.ImageFilter ^
  --enable-plugin=tk-inter ^
  %1

ENDLOCAL