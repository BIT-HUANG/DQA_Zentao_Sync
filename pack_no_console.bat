@echo off
setlocal

:: Define source directory and target directory
set PROGRAM_NAME=DQA_SYNC
set ENTRY_DIR=%~dp0
echo %ENTRY_DIR%

:: Start packaging the program
echo Packaging %PROGRAM_NAME%.exe (no console mode)...
cd "%ENTRY_DIR%"
echo y | pyinstaller --onefile --noupx --clean --log-level INFO --noconfirm --noconsole ^
--hidden-import=json --hidden-import=colorama --hidden-import=jira --hidden-import=translate --hidden-import=openpyxl ^
:: ======== Flask相关隐式依赖 ========
--hidden-import=flask --hidden-import=flask.json --hidden-import=werkzeug --hidden-import=jinja2 --hidden-import=markupsafe ^
:: ======== 根目录的portal.py ========
--add-data "portal.py;." ^
:: ======== 原有libmirror所有配置  ========
--add-data "libmirror/mstr.py;." ^
--add-data "libmirror/mconfig.py;." ^
--add-data "libmirror/mio.py;." ^
--add-data "libmirror/mlogger.py;." ^
--add-data "libmirror/mpath.py;." ^
--add-data "libmirror/mjira/const.py;mjira" ^
--add-data "libmirror/mjira/field.py;mjira" ^
--add-data "libmirror/mjira/issue.py;mjira" ^
--add-data "libmirror/mjira/http.py;mjira" ^
--add-data "libmirror/mjira/net_sony.py;mjira" ^
--add-data "libmirror/mzentao/*.py;mzentao" ^
%PROGRAM_NAME%.py
if %errorlevel% neq 0 (
    echo Packaging failed, please check pyinstaller configuration!
    pause
    exit /b 1
)

echo Operation Completed
pause