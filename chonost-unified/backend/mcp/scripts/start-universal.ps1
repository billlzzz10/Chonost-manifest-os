#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Universal File System MCP Server Launcher
.DESCRIPTION
    Launcher script สำหรับ Universal File System MCP Server
    รองรับการจัดการและวิเคราะห์โครงสร้างโฟลเดอร์ทุกรูปแบบ
.PARAMETER Mode
    โหมดการทำงาน (server, test, config)
.PARAMETER Platform
    แพลตฟอร์มที่ต้องการทดสอบ (local, cloud, mobile, network)
.EXAMPLE
    .\start-universal.ps1 -Mode server
    .\start-universal.ps1 -Mode test -Platform local
    .\start-universal.ps1 -Mode config
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("server", "test", "config", "help")]
    [string]$Mode = "server",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("local", "cloud", "mobile", "network", "all")]
    [string]$Platform = "all"
)

# Color functions
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    
    $Colors = @{
        "Success" = "Green"
        "Error" = "Red"
        "Warning" = "Yellow"
        "Info" = "Cyan"
        "Header" = "Magenta"
        "SubHeader" = "Blue"
    }
    
    $ColorCode = $Colors[$Color]
    if (-not $ColorCode) { $ColorCode = "White" }
    
    Write-Host $Text -ForegroundColor $ColorCode
}

function Show-Header {
    Write-ColorText "╔══════════════════════════════════════════════════════════════╗" "Header"
    Write-ColorText "║                🌐 Universal File System MCP Server          ║" "Header"
    Write-ColorText "║                    Version 3.0.0 - Orion Senior Dev         ║" "Header"
    Write-ColorText "╚══════════════════════════════════════════════════════════════╝" "Header"
    Write-Host ""
}

function Show-PlatformInfo {
    Write-ColorText "📋 รองรับแพลตฟอร์ม:" "SubHeader"
    Write-ColorText "   🖥️  Desktop: Windows, macOS, Linux" "Info"
    Write-ColorText "   ☁️  Cloud: Google Drive, Dropbox, OneDrive, AWS S3" "Info"
    Write-ColorText "   📱 Mobile: Android, iOS" "Info"
    Write-ColorText "   🌐 Network: NAS, FTP, SFTP, SMB" "Info"
    Write-Host ""
}

function Show-ModeInfo {
    Write-ColorText "🎯 โหมดการทำงาน:" "SubHeader"
    Write-ColorText "   server  - เริ่มต้น MCP Server" "Info"
    Write-ColorText "   test    - ทดสอบการทำงาน" "Info"
    Write-ColorText "   config  - จัดการการตั้งค่า" "Info"
    Write-ColorText "   help    - แสดงความช่วยเหลือ" "Info"
    Write-Host ""
}

function Test-Prerequisites {
    Write-ColorText "🔍 ตรวจสอบ Prerequisites..." "Info"
    
    # Check Python
    try {
        # Try multiple Python paths
        $pythonPaths = @(
            "python",
            "py",
            "python3",
            ".\venv\Scripts\python.exe",
            "C:\Python312\python.exe",
            "C:\Python311\python.exe",
            "C:\Python310\python.exe",
            "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe",
            "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
            "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python310\python.exe"
        )
        
        $pythonFound = $false
        foreach ($pythonPath in $pythonPaths) {
            try {
                if ($pythonPath -eq "python" -or $pythonPath -eq "py" -or $pythonPath -eq "python3") {
                    $pythonVersion = & $pythonPath --version 2>&1
                } else {
                    if (Test-Path $pythonPath) {
                        $pythonVersion = & $pythonPath --version 2>&1
                    } else {
                        continue
                    }
                }
                
                if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
                    $version = $matches[1]
                    Write-ColorText "✅ Python: $version (จาก $pythonPath)" "Success"
                    $script:PythonExecutable = $pythonPath
                    $pythonFound = $true
                    break
                }
            } catch {
                continue
            }
        }
        
        if (-not $pythonFound) {
            Write-ColorText "❌ Python ไม่พบในระบบ" "Error"
            Write-ColorText "💡 ลองติดตั้ง Python จาก https://python.org" "Info"
            return $false
        }
    } catch {
        Write-ColorText "❌ Python ไม่พบ" "Error"
        return $false
    }
    
    # Check required files
    $requiredFiles = @(
        "src\server\universal_fs_mcp_server.py",
        "src\core\file_system_analyzer.py",
        "datasets\universal_mcp_config.json"
    )
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-ColorText "✅ $file" "Success"
        } else {
            Write-ColorText "❌ $file ไม่พบ" "Error"
            return $false
        }
    }
    
    # Check dependencies
    try {
        $modules = @("asyncio", "requests", "pathlib")
        foreach ($module in $modules) {
            & $script:PythonExecutable -c "import $module" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorText "✅ $module" "Success"
            } else {
                Write-ColorText "⚠️  $module - อาจต้องติดตั้ง" "Warning"
            }
        }
    } catch {
        Write-ColorText "⚠️  ไม่สามารถตรวจสอบ dependencies ได้" "Warning"
    }
    
    Write-Host ""
    return $true
}

function Start-MCPServer {
    Write-ColorText "🚀 เริ่มต้น Universal MCP Server..." "Info"
    
    # Check if server is already running
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -eq "python" -and $_.CommandLine -like "*universal_fs_mcp_server.py*"
    }
    
    if ($processes) {
        Write-ColorText "⚠️  MCP Server กำลังทำงานอยู่" "Warning"
        $response = Read-Host "ต้องการหยุดและเริ่มใหม่? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            foreach ($process in $processes) {
                Stop-Process -Id $process.Id -Force
                Write-ColorText "✅ หยุด process: $($process.Id)" "Success"
            }
        } else {
            Write-ColorText "❌ ยกเลิกการเริ่มต้น" "Error"
            return
        }
    }
    
    try {
        Write-ColorText "📡 เริ่มต้น server บน stdin/stdout..." "Info"
        Write-ColorText "💡 ใช้ Ctrl+C เพื่อหยุด server" "Info"
        Write-Host ""
        
        # Start the server
        & $script:PythonExecutable src\server\universal_fs_mcp_server.py
        
    } catch {
        Write-ColorText "❌ เกิดข้อผิดพลาดในการเริ่มต้น server: $($_.Exception.Message)" "Error"
    }
}

function Test-Platform {
    param([string]$Platform)
    
    Write-ColorText "🧪 ทดสอบแพลตฟอร์ม: $Platform" "Info"
    
    switch ($Platform) {
        "local" {
            Test-LocalPlatform
        }
        "cloud" {
            Test-CloudPlatform
        }
        "mobile" {
            Test-MobilePlatform
        }
        "network" {
            Test-NetworkPlatform
        }
        "all" {
            Test-LocalPlatform
            Test-CloudPlatform
            Test-MobilePlatform
            Test-NetworkPlatform
        }
    }
}

function Test-LocalPlatform {
    Write-ColorText "🖥️  ทดสอบ Local Platform..." "SubHeader"
    
    # Test current directory
    $testPath = Get-Location
    Write-ColorText "   📁 Test path: $testPath" "Info"
    
    # Test file system info
    $drive = Get-PSDrive C -ErrorAction SilentlyContinue
    if ($drive) {
        Write-ColorText "   💾 Drive C: $($drive.Used) / $($drive.Free) bytes" "Info"
    }
    
    # Test file operations
    try {
        $testFile = "test_universal_mcp.txt"
        "Test content" | Out-File -FilePath $testFile -Encoding UTF8
        if (Test-Path $testFile) {
            Write-ColorText "   ✅ File creation test: PASS" "Success"
            Remove-Item $testFile -Force
        }
    } catch {
        Write-ColorText "   ❌ File creation test: FAIL" "Error"
    }
    
    Write-Host ""
}

function Test-CloudPlatform {
    Write-ColorText "☁️  ทดสอบ Cloud Platform..." "SubHeader"
    
    # Check for cloud credentials
    $configFile = "datasets\universal_mcp_config.json"
    if (Test-Path $configFile) {
        try {
            $config = Get-Content $configFile | ConvertFrom-Json
            $cloudProviders = $config.supported_platforms.cloud.PSObject.Properties.Name
            Write-ColorText "   📋 รองรับ Cloud Providers: $($cloudProviders -join ', ')" "Info"
        } catch {
            Write-ColorText "   ❌ ไม่สามารถอ่าน config file ได้" "Error"
        }
    } else {
        Write-ColorText "   ❌ Config file ไม่พบ" "Error"
    }
    
    Write-ColorText "   ⚠️  Cloud testing ต้องการ credentials" "Warning"
    Write-Host ""
}

function Test-MobilePlatform {
    Write-ColorText "📱 ทดสอบ Mobile Platform..." "SubHeader"
    
    # Check for mobile development tools
    $adbPath = Get-Command adb -ErrorAction SilentlyContinue
    if ($adbPath) {
        Write-ColorText "   ✅ ADB (Android Debug Bridge) พบ" "Success"
    } else {
        Write-ColorText "   ⚠️  ADB ไม่พบ - Android testing ไม่พร้อม" "Warning"
    }
    
    # Check for iOS development tools (on macOS)
    if ($IsMacOS -or $env:OS -eq "Darwin") {
        $xcodePath = Get-Command xcodebuild -ErrorAction SilentlyContinue
        if ($xcodePath) {
            Write-ColorText "   ✅ Xcode พบ" "Success"
        } else {
            Write-ColorText "   ⚠️  Xcode ไม่พบ - iOS testing ไม่พร้อม" "Warning"
        }
    } else {
        Write-ColorText "   ℹ️  iOS testing เฉพาะ macOS" "Info"
    }
    
    Write-Host ""
}

function Test-NetworkPlatform {
    Write-ColorText "🌐 ทดสอบ Network Platform..." "SubHeader"
    
    # Test network connectivity
    try {
        $pingResult = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
        if ($pingResult) {
            Write-ColorText "   ✅ Network connectivity: PASS" "Success"
        } else {
            Write-ColorText "   ❌ Network connectivity: FAIL" "Error"
        }
    } catch {
        Write-ColorText "   ❌ Network connectivity: FAIL" "Error"
    }
    
    # Check for network tools
    $ftpClient = Get-Command ftp -ErrorAction SilentlyContinue
    if ($ftpClient) {
        Write-ColorText "   ✅ FTP client พบ" "Success"
    } else {
        Write-ColorText "   ⚠️  FTP client ไม่พบ" "Warning"
    }
    
    Write-Host ""
}

function Show-Configuration {
    Write-ColorText "⚙️  การตั้งค่า Universal MCP Server" "SubHeader"
    
    $configFile = "universal_mcp_config.json"
    if (Test-Path $configFile) {
        try {
            $config = Get-Content $configFile | ConvertFrom-Json
            
            Write-ColorText "📋 Server Info:" "Info"
            Write-ColorText "   Name: $($config.server_info.name)" "Info"
            Write-ColorText "   Version: $($config.server_info.version)" "Info"
            Write-ColorText "   Description: $($config.server_info.description)" "Info"
            
            Write-Host ""
            Write-ColorText "🔧 Performance Settings:" "Info"
            Write-ColorText "   Max Concurrent Scans: $($config.performance_settings.max_concurrent_scans)" "Info"
            Write-ColorText "   Max File Size: $($config.performance_settings.max_file_size_mb) MB" "Info"
            Write-ColorText "   Timeout: $($config.performance_settings.timeout_seconds) seconds" "Info"
            
            Write-Host ""
            Write-ColorText "🔒 Security Settings:" "Info"
            Write-ColorText "   Encrypt Credentials: $($config.security_settings.encrypt_credentials)" "Info"
            Write-ColorText "   Secure Connections Only: $($config.security_settings.secure_connections_only)" "Info"
            Write-ColorText "   Session Timeout: $($config.security_settings.session_timeout_minutes) minutes" "Info"
            
        } catch {
            Write-ColorText "❌ ไม่สามารถอ่าน config file ได้: $($_.Exception.Message)" "Error"
        }
    } else {
        Write-ColorText "❌ Config file ไม่พบ: $configFile" "Error"
    }
    
    Write-Host ""
    Write-ColorText "💡 ใช้ text editor แก้ไข universal_mcp_config.json เพื่อปรับแต่งการตั้งค่า" "Info"
}

function Show-Help {
    Show-Header
    Show-PlatformInfo
    Show-ModeInfo
    
    Write-ColorText "📖 ตัวอย่างการใช้งาน:" "SubHeader"
    Write-ColorText "   .\start-universal.ps1                    # เริ่มต้น server" "Info"
    Write-ColorText "   .\start-universal.ps1 -Mode test         # ทดสอบทุกแพลตฟอร์ม" "Info"
    Write-ColorText "   .\start-universal.ps1 -Mode test -Platform local" "Info"
    Write-ColorText "   .\start-universal.ps1 -Mode config       # ดูการตั้งค่า" "Info"
    Write-ColorText "   .\start-universal.ps1 -Mode help         # แสดงความช่วยเหลือ" "Info"
    
    Write-Host ""
    Write-ColorText "🔗 Documentation:" "SubHeader"
    Write-ColorText "   📄 UNIVERSAL_MCP_README.md" "Info"
    Write-ColorText "   📄 universal_mcp_config.json" "Info"
    
    Write-Host ""
    Write-ColorText "🌐 Features:" "SubHeader"
    Write-ColorText "   • Universal Directory Scanning" "Info"
    Write-ColorText "   • Cross-Platform File Search" "Info"
    Write-ColorText "   • Cloud Storage Integration" "Info"
    Write-ColorText "   • Mobile Storage Analysis" "Info"
    Write-ColorText "   • Network Storage Connection" "Info"
    Write-ColorText "   • UnicornX OS Integration" "Info"
}

# Main execution
Show-Header

switch ($Mode) {
    "server" {
        if (Test-Prerequisites) {
            Start-MCPServer
        } else {
            Write-ColorText "❌ Prerequisites ไม่ครบถ้วน" "Error"
            exit 1
        }
    }
    "test" {
        if (Test-Prerequisites) {
            Test-Platform -Platform $Platform
        } else {
            Write-ColorText "❌ Prerequisites ไม่ครบถ้วน" "Error"
            exit 1
        }
    }
    "config" {
        Show-Configuration
    }
    "help" {
        Show-Help
    }
    default {
        Write-ColorText "❌ โหมดไม่ถูกต้อง: $Mode" "Error"
        Show-Help
        exit 1
    }
}

Write-Host ""
Write-ColorText "✨ Universal File System MCP Server - Complete!" "Success"
