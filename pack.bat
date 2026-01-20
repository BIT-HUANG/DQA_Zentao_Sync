@echo off
setlocal

:: Define source directory and target directory
set PROGRAM_NAME=DQA_SYNC
set ENTRY_DIR=%~dp0
echo %ENTRY_DIR%

:: Start packaging the program
echo Packaging %PROGRAM_NAME%.exe...
cd "%ENTRY_DIR%"
echo y | pyinstaller --onefile --noupx --clean --log-level INFO --noconfirm ^
:: ========== 原有基础依赖 ==========
--hidden-import=json --hidden-import=colorama --hidden-import=jira --hidden-import=translate --hidden-import=openpyxl ^
:: ========== Flask相关依赖（补充完整） ==========
--hidden-import=flask --hidden-import=flask.json --hidden-import=werkzeug --hidden-import=jinja2 ^
--hidden-import=werkzeug.serving --hidden-import=werkzeug._internal --hidden-import=click ^
:: ========== ngrok相关依赖（核心新增） ==========
--hidden-import=ngrok --hidden-import=ngrok._ffi --hidden-import=ngrok._impl --hidden-import=ngrok.api ^
--hidden-import=asyncio --hidden-import=threading --hidden-import=ctypes ^
:: ========== 状态管理相关依赖（新增） ==========
--hidden-import=psutil  :: 可选：如果用了psutil强制终止ngrok进程则添加 ^
:: ========== 添加所有新增文件到打包目录（核心） ==========
--add-data "portal.py;." ^
--add-data "service_manager.py;." ^  :: 新增服务管理模块 ^
:: ========== 原有libmirror相关的add-data配置 ==========
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