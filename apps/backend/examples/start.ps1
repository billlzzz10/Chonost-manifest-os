#!/usr/bin/env powershell
<#
.SYNOPSIS
    File System MCP Project Launcher (Simple Version)
.DESCRIPTION
    PowerShell script ง่ายๆ สำหรับเปิดแอปพลิเคชันต่างๆ
.PARAMETER App
    ชื่อแอปที่ต้องการเปิด
#>

param(
    [Parameter(Position=0)]
    [string]$App
)

# ฟังก์ชันแสดงความช่วยเหลือ
function Show-Help {
    Write-Host ""
    Write-Host "🚀 File System MCP Project Launcher" -ForegroundColor Magenta
    Write-Host ("=" * 50) -ForegroundColor Magenta
    Write-Host ""
    Write-Host "📋 คำสั่งที่ใช้งานได้:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  chat      - เปิดแอปแชตพื้นฐาน" -ForegroundColor Green
    Write-Host "  advanced  - เปิดแอปแชตขั้นสูง" -ForegroundColor Green
    Write-Host "  ai        - เปิดแอปแชตที่รวม AI" -ForegroundColor Green
    Write-Host "  dataset   - สร้างชุดข้อมูลฝึก AI" -ForegroundColor Green
    Write-Host "  unified   - เปิดแอป Unified Chat" -ForegroundColor Green
    Write-Host "  test      - ทดสอบ AI connection" -ForegroundColor Green
    Write-Host "  ollama    - ทดสอบ AI connection (alias)" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 ตัวอย่างการใช้งาน:" -ForegroundColor Cyan
    Write-Host "  .\start.ps1 chat           # เปิดแอปแชตพื้นฐาน"
    Write-Host "  .\start.ps1 ai             # เปิดแอปแชตที่รวม AI"
    Write-Host "  .\start.ps1 dataset        # สร้างชุดข้อมูล"
    Write-Host ""
}

# ฟังก์ชันตรวจสอบไฟล์
function Test-FileExists {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        Write-Host "✅ พบไฟล์: $FilePath" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ ไม่พบไฟล์: $FilePath" -ForegroundColor Red
        return $false
    }
}

# ฟังก์ชันเรียกใช้ Python
function Invoke-PythonScript {
    param([string]$ScriptPath)
    
    if (Test-Path "venv\Scripts\Activate.ps1") {
        Write-Host "📦 ใช้ Virtual Environment" -ForegroundColor Yellow
        & venv\Scripts\Activate.ps1
        python $ScriptPath
    } else {
        Write-Host "🌐 ใช้ Python global" -ForegroundColor Yellow
        python $ScriptPath
    }
}

# เริ่มต้น
Write-Host ""
Write-Host "🚀 File System MCP Project Launcher" -ForegroundColor Magenta
Write-Host ("=" * 50) -ForegroundColor Magenta
Write-Host ""

# ตรวจสอบ parameter
if (-not $App -or $App -eq "help" -or $App -eq "-h") {
    Show-Help
    exit
}

# ตรวจสอบ Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python ไม่พบ" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Python ไม่พบ" -ForegroundColor Red
    exit 1
}

# เลือกแอป
switch ($App.ToLower()) {
    "chat" {
        Write-Host "💬 เปิดแอปแชตพื้นฐาน..." -ForegroundColor Cyan
        if (Test-FileExists "desktop_chat_app.py") {
            Invoke-PythonScript "desktop_chat_app.py"
        }
    }
    "advanced" {
        Write-Host "🔧 เปิดแอปแชตขั้นสูง..." -ForegroundColor Cyan
        if (Test-FileExists "advanced_chat_app.py") {
            Invoke-PythonScript "advanced_chat_app.py"
        }
    }
    "ai" {
        Write-Host "🤖 เปิดแอปแชตที่รวม AI..." -ForegroundColor Cyan
        if (Test-FileExists "ai_enhanced_chat_app.py") {
            Invoke-PythonScript "ai_enhanced_chat_app.py"
        }
    }
    "dataset" {
        Write-Host "📊 สร้างชุดข้อมูลฝึก AI..." -ForegroundColor Cyan
        if (Test-FileExists "utils/generate_fs_training_data.py") {
            Invoke-PythonScript "utils/generate_fs_training_data.py"
            Write-Host ""
            Write-Host "✅ เสร็จสิ้น! ตรวจสอบไฟล์ที่สร้าง:" -ForegroundColor Green
            Write-Host "  • file_system_training_dataset.json" -ForegroundColor Gray
            Write-Host "  • expanded_dataset.json" -ForegroundColor Gray
            Write-Host "  • test_dataset.json" -ForegroundColor Gray
        }
    }
    "unified" {
        Write-Host "🚀 เปิดแอป Unified Chat..." -ForegroundColor Cyan
        if (Test-FileExists "apps/unified_chat_app.py") {
            Invoke-PythonScript "apps/unified_chat_app.py"
        }
    }
    { $_ -in @("test", "ollama") } {
        Write-Host "🧪 ทดสอบการเชื่อมต่อ AI ผ่าน Unified App..." -ForegroundColor Cyan
        if (Test-FileExists "apps/unified_chat_app.py") {
            Invoke-PythonScript "apps/unified_chat_app.py"
        }
    }
    default {
        Write-Host "❌ แอป '$App' ไม่รู้จัก" -ForegroundColor Red
        Write-Host "💡 ใช้ .\start.ps1 help เพื่อดูคำสั่งที่ใช้งานได้" -ForegroundColor Yellow
    }
}
