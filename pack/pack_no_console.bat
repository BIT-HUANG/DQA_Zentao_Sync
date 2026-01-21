@echo off
setlocal

:: Define source directory and target directory
set PROGRAM_NAME=DQA_SYNC
set OUTPUT_EXE_NAME=DQA_SYNC_NO_CONSOLE
set ENTRY_DIR=%~dp0..\
echo %ENTRY_DIR%

:: Start packaging the program
echo Packaging %PROGRAM_NAME%.exe (no console mode)...
cd "%ENTRY_DIR%"
echo y | pyinstaller --onedir --noupx --clean --log-level INFO --noconfirm --noconsole ^
--name %OUTPUT_EXE_NAME% ^
--hidden-import=json --hidden-import=colorama --hidden-import=jira --hidden-import=translate --hidden-import=openpyxl ^
--hidden-import=flask --hidden-import=flask.json --hidden-import=werkzeug --hidden-import=jinja2 ^
--hidden-import=werkzeug.serving --hidden-import=werkzeug._internal --hidden-import=click ^
--hidden-import=ngrok --hidden-import=ngrok._ffi --hidden-import=ngrok._impl --hidden-import=ngrok.api ^
--hidden-import=asyncio --hidden-import=threading --hidden-import=ctypes ^
--hidden-import=psutil ^
--add-data "portal.py;." ^
--add-data "service_manager.py;." ^
--add-data "system_setting_ui.py;." ^
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
--add-data "README.md;." ^
%PROGRAM_NAME%.py
if %errorlevel% neq 0 (
    echo Packaging failed, please check pyinstaller configuration!
    pause
    exit /b 1
)

echo Operation Completed
pause