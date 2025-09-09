@echo off
echo 🚀 Building Chonost Desktop App
echo ===============================

cd /d "%~dp0"

echo 📦 Installing dependencies...
cd packages\frontend
call npm install --ignore-workspace
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

echo 🏗️ Building frontend...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Failed to build frontend
    exit /b 1
)

echo 💻 Building desktop app with Tauri...
call npm run tauri build
if %errorlevel% neq 0 (
    echo ❌ Failed to build desktop app
    exit /b 1
)

echo ✅ Build completed successfully!
echo Check packages\frontend\src-tauri\target\release\ for the executable

pause
