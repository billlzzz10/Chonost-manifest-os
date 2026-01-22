@echo off
REM File System MCP Project Launcher (Windows Batch)
REM สำหรับ Windows ที่ไม่สามารถรัน PowerShell ได้

title File System MCP Launcher

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="-h" goto help
if "%1"=="--help" goto help

echo.
echo 🚀 File System MCP Project Launcher
echo ==================================================
echo.

REM ตรวจสอบ Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ไม่พบ กรุณาติดตั้ง Python ก่อน
    pause
    exit /b 1
)
echo ✅ Python พบแล้ว

REM ตรวจสอบ Virtual Environment
if exist "venv\Scripts\activate.bat" (
    echo ✅ Virtual Environment พบ
    set USE_VENV=1
) else (
    echo ⚠️ Virtual Environment ไม่พบ ใช้ Python global
    set USE_VENV=0
)

echo.

REM เลือกแอป
if "%1"=="chat" goto start_chat
if "%1"=="advanced" goto start_advanced
if "%1"=="ai" goto start_ai
if "%1"=="dataset" goto start_dataset
if "%1"=="test" goto start_test
if "%1"=="ollama" goto start_test

echo ❌ แอป '%1' ไม่รู้จัก
goto help

:start_chat
echo 💬 เปิดแอปแชตพื้นฐาน...
if not exist "desktop_chat_app.py" (
    echo ❌ ไม่พบไฟล์ desktop_chat_app.py
    pause
    exit /b 1
)
if %USE_VENV%==1 (
    call venv\Scripts\activate.bat
)
python desktop_chat_app.py
goto end

:start_advanced
echo 🔧 เปิดแอปแชตขั้นสูง...
if not exist "advanced_chat_app.py" (
    echo ❌ ไม่พบไฟล์ advanced_chat_app.py
    pause
    exit /b 1
)
if %USE_VENV%==1 (
    call venv\Scripts\activate.bat
)
python advanced_chat_app.py
goto end

:start_ai
echo 🤖 เปิดแอปแชตที่รวม AI...
if not exist "ai_enhanced_chat_app.py" (
    echo ❌ ไม่พบไฟล์ ai_enhanced_chat_app.py
    pause
    exit /b 1
)
if %USE_VENV%==1 (
    call venv\Scripts\activate.bat
)
python ai_enhanced_chat_app.py
goto end

:start_dataset
echo 📊 สร้างชุดข้อมูลฝึก AI...
if not exist "utils\synthetic_fs_dataset_generator.py" (
    echo ❌ ไม่พบไฟล์ utils\synthetic_fs_dataset_generator.py
    pause
    exit /b 1
)
if %USE_VENV%==1 (
    call venv\Scripts\activate.bat
)
python utils\synthetic_fs_dataset_generator.py
echo.
echo ✅ เสร็จสิ้น! ตรวจสอบไฟล์ที่สร้าง:
echo   • file_system_training_dataset.json
echo   • expanded_dataset.json
echo   • test_dataset.json
pause
goto end

:start_test
echo 🧪 ทดสอบการเชื่อมต่อ AI ผ่าน Unified App...
if not exist "apps\unified_chat_app.py" (
    echo ❌ ไม่พบไฟล์ apps\unified_chat_app.py
    pause
    exit /b 1
)
if %USE_VENV%==1 (
    call venv\Scripts\activate.bat
)
python apps/unified_chat_app.py
pause
goto end

:help
echo.
echo 🚀 File System MCP Project Launcher
echo ==================================================
echo.
echo 📋 คำสั่งที่ใช้งานได้:
echo.
echo   chat       - เปิดแอปแชตพื้นฐาน
echo   advanced   - เปิดแอปแชตขั้นสูง
echo   ai         - เปิดแอปแชตที่รวม AI
echo   unified    - เปิดแอป Unified Chat
echo   dataset    - สร้างชุดข้อมูลฝึก AI
echo   test       - ทดสอบการเชื่อมต่อ AI
echo   ollama     - ทดสอบการเชื่อมต่อ AI (alias)
echo.
echo 💡 ตัวอย่างการใช้งาน:
echo   run.bat chat           # เปิดแอปแชตพื้นฐาน
echo   run.bat ai             # เปิดแอปแชตที่รวม AI
echo   run.bat dataset        # สร้างชุดข้อมูล
echo   run.bat test           # ทดสอบ Ollama
echo.
pause

:end
