#!/usr/bin/env powershell
<#
.SYNOPSIS
    File System MCP Project Launcher
    เครื่องมือเปิดโปรแกรมต่างๆ ในโปรเจค File System MCP

.DESCRIPTION
    PowerShell script สำหรับเปิดแอปพลิเคชันต่างๆ ในโปรเจค
    รองรับการเปิดหลายแอปพร้อมกันและการตั้งค่าต่างๆ

.PARAMETER App
    ชื่อแอปที่ต้องการเปิด (chat, advanced, ai, dataset, test, ollama)

.PARAMETER All
    เปิดแอปทั้งหมดพร้อมกัน

.PARAMETER Help
    แสดงความช่วยเหลือ

.EXAMPLE
    .\run.ps1 chat
    เปิดแอปแชตพื้นฐาน

.EXAMPLE
    .\run.ps1 ai
    เปิดแอปแชตที่รวม AI

.EXAMPLE
    .\run.ps1 -All
    เปิดแอปทั้งหมด
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("chat", "advanced", "ai", "dataset", "test", "ollama", "help")]
    [string]$App,
    
    [switch]$All,
    [switch]$Help
)

# ตัวแปรสีสำหรับการแสดงผล
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Title = "Magenta"
}

# ฟังก์ชันแสดงข้อความสี
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Colors[$Color]
}

# ฟังก์ชันแสดงหัวข้อ
function Show-Header {
    Write-Host ""
    Write-ColorText "🚀 File System MCP Project Launcher" "Title"
    Write-ColorText "=" * 50 "Title"
    Write-Host ""
}

# ฟังก์ชันแสดงความช่วยเหลือ
function Show-Help {
    Show-Header
    Write-ColorText "📋 คำสั่งที่ใช้งานได้:" "Info"
    Write-Host ""
    
    $commands = @(
        @("chat", "เปิดแอปแชตพื้นฐาน", "desktop_chat_app.py")
        @("advanced", "เปิดแอปแชตขั้นสูง", "advanced_chat_app.py")
        @("ai", "เปิดแอปแชตที่รวม AI", "ai_enhanced_chat_app.py")
        @("unified", "เปิดแอป Unified Chat ที่รวมทุกอย่าง", "unified_chat_app.py")
        @("dataset", "สร้างชุดข้อมูลฝึก AI", "filesystem_tool_dataset_generator.py")
        @("test", "ทดสอบ AI connection ผ่าน Unified App", "unified_chat_app.py")
        @("ollama", "ทดสอบ AI connection (alias)", "unified_chat_app.py")
    )
    
    foreach ($cmd in $commands) {
        Write-Host "  " -NoNewline
        Write-ColorText "$($cmd[0].PadRight(10))" "Success"
        Write-Host " - $($cmd[1])" -NoNewline
        Write-Host " ($($cmd[2]))" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-ColorText "🔧 ตัวเลือกพิเศษ:" "Info"
    Write-Host "  -All       - เปิดแอปทั้งหมด"
    Write-Host "  -Help      - แสดงความช่วยเหลือ"
    Write-Host ""
    
    Write-ColorText "💡 ตัวอย่างการใช้งาน:" "Info"
    Write-Host "  .\run.ps1 chat           # เปิดแอปแชตพื้นฐาน"
    Write-Host "  .\run.ps1 ai             # เปิดแอปแชตที่รวม AI"
    Write-Host "  .\run.ps1 dataset        # สร้างชุดข้อมูล"
    Write-Host "  .\run.ps1 -All           # เปิดแอปทั้งหมด"
    Write-Host ""
}

# ฟังก์ชันตรวจสอบการติดตั้ง
function Test-Requirements {
    Write-ColorText "🔍 ตรวจสอบการติดตั้ง..." "Info"
    
    # ตรวจสอบ Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Python: $pythonVersion" "Success"
        } else {
            Write-ColorText "❌ Python ไม่พบ" "Error"
            return $false
        }
    } catch {
        Write-ColorText "❌ Python ไม่พบ" "Error"
        return $false
    }
    
    # ตรวจสอบ Virtual Environment
    if (Test-Path "venv\Scripts\Activate.ps1") {
        Write-ColorText "✅ Virtual Environment พบ" "Success"
    } else {
        Write-ColorText "⚠️ Virtual Environment ไม่พบ" "Warning"
        Write-ColorText "💡 สร้าง venv ด้วยคำสั่ง: python -m venv venv" "Info"
    }
    
    # ตรวจสอบไฟล์หลัก
    $requiredFiles = @(
        "file_system_analyzer.py",
        "desktop_chat_app.py",
        "advanced_chat_app.py",
        "filesystem_tool_dataset_generator.py"
    )
    
    $missingFiles = @()
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-ColorText "✅ $file" "Success"
        } else {
            Write-ColorText "❌ $file ไม่พบ" "Error"
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-ColorText "❌ ไฟล์หายไป: $($missingFiles -join ', ')" "Error"
        return $false
    }
    
    Write-Host ""
    return $true
}

# ฟังก์ชันเปิดแอป
function Start-Application {
    param(
        [string]$AppName,
        [string]$ScriptPath,
        [string]$Description
    )
    
    Write-ColorText "🚀 เปิด $Description..." "Info"
    
    # เช็คว่ามี Virtual Environment หรือไม่
    if (Test-Path "venv\Scripts\Activate.ps1") {
        # ใช้ Virtual Environment
        $command = "& venv\Scripts\Activate.ps1; python $ScriptPath"
        Write-ColorText "📦 ใช้ Virtual Environment" "Info"
    } else {
        # ใช้ Python global
        $command = "python $ScriptPath"
        Write-ColorText "🌐 ใช้ Python global" "Warning"
    }
    
    try {
        # เปิดในหน้าต่างใหม่
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
        Write-ColorText "✅ เปิด $Description สำเร็จ" "Success"
        Write-Host ""
    } catch {
        Write-ColorText "❌ ไม่สามารถเปิด $Description ได้: $($_.Exception.Message)" "Error"
        Write-Host ""
    }
}

# ฟังก์ชันเปิดแอปทั้งหมด
function Start-AllApplications {
    Write-ColorText "🚀 เปิดแอปทั้งหมด..." "Title"
    Write-Host ""
    
    $apps = @(
        @("chat", "desktop_chat_app.py", "แอปแชตพื้นฐาน")
        @("advanced", "advanced_chat_app.py", "แอปแชตขั้นสูง")
        @("ai", "ai_enhanced_chat_app.py", "แอปแชตที่รวม AI")
    )
    
    foreach ($app in $apps) {
        Start-Application $app[0] $app[1] $app[2]
        Start-Sleep -Seconds 1  # รอสักครู่ระหว่างการเปิดแอป
    }
    
    Write-ColorText "🎉 เปิดแอปทั้งหมดเสร็จสิ้น!" "Success"
}

# ฟังก์ชันหลัก
function Main {
    # แสดงความช่วยเหลือ
    if ($Help -or $App -eq "help" -or (-not $App -and -not $All)) {
        Show-Help
        return
    }
    
    Show-Header
    
    # ตรวจสอบการติดตั้ง
    if (-not (Test-Requirements)) {
        Write-ColorText "❌ การตรวจสอบล้มเหลว กรุณาแก้ไขปัญหาก่อนใช้งาน" "Error"
        return
    }
    
    # เปิดแอปทั้งหมด
    if ($All) {
        Start-AllApplications
        return
    }
    
    # เปิดแอปตามที่เลือก
    switch ($App.ToLower()) {
        "chat" {
            Start-Application "chat" "desktop_chat_app.py" "แอปแชตพื้นฐาน"
        }
        "advanced" {
            Start-Application "advanced" "advanced_chat_app.py" "แอปแชตขั้นสูง"
        }
        "ai" {
            Start-Application "ai" "ai_enhanced_chat_app.py" "แอปแชตที่รวม AI"
        }
        "dataset" {
            Write-ColorText "📊 สร้างชุดข้อมูลฝึก AI..." "Info"
            if (Test-Path "venv\Scripts\Activate.ps1") {
                & venv\Scripts\Activate.ps1
                python filesystem_tool_dataset_generator.py
            } else {
                python filesystem_tool_dataset_generator.py
            }
        }
        "unified" {
            Start-Application "unified" "apps/unified_chat_app.py" "แอป Unified Chat"
        }
        { $_ -eq "test" -or $_ -eq "ollama" } {
            Write-ColorText "🧪 ทดสอบการเชื่อมต่อ AI ผ่าน Unified App..." "Info"
            Start-Application "unified" "apps/unified_chat_app.py" "แอป Unified Chat"
        }
        default {
            Write-ColorText "❌ แอป '$App' ไม่รู้จัก" "Error"
            Write-ColorText "💡 ใช้ .\run.ps1 -Help เพื่อดูคำสั่งที่ใช้งานได้" "Info"
        }
    }
}

# เรียกใช้ฟังก์ชันหลัก
Main
