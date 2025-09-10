#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Docker Launcher สำหรับ Universal File System MCP Server
.DESCRIPTION
    สคริปต์สำหรับจัดการ Docker containers ของ Universal MCP Server
.PARAMETER Action
    การกระทำ (build, start, stop, restart, logs, shell, clean)
.PARAMETER Mode
    โหมดการทำงาน (dev, prod)
.EXAMPLE
    .\start-docker.ps1 -Action build
    .\start-docker.ps1 -Action start -Mode prod
    .\start-docker.ps1 -Action logs
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("build", "start", "stop", "restart", "logs", "shell", "clean", "status")]
    [string]$Action = "start",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "prod")]
    [string]$Mode = "dev"
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
    Write-ColorText "║           🐳 Docker Universal File System MCP Server        ║" "Header"
    Write-ColorText "║                    Version 3.0.0 - Orion Senior Dev         ║" "Header"
    Write-ColorText "╚══════════════════════════════════════════════════════════════╝" "Header"
    Write-Host ""
}

function Test-DockerPrerequisites {
    Write-ColorText "🔍 ตรวจสอบ Docker Prerequisites..." "Info"
    
    # Check if Docker is installed
    try {
        $dockerVersion = docker --version 2>&1
        if ($dockerVersion -match "Docker version") {
            Write-ColorText "✅ Docker: $dockerVersion" "Success"
        } else {
            Write-ColorText "❌ Docker ไม่พบหรือเวอร์ชันไม่ถูกต้อง" "Error"
            return $false
        }
    } catch {
        Write-ColorText "❌ Docker ไม่พบ" "Error"
        Write-ColorText "💡 ติดตั้ง Docker Desktop จาก https://docker.com" "Info"
        return $false
    }
    
    # Check if Docker is running
    try {
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Docker daemon กำลังทำงาน" "Success"
        } else {
            Write-ColorText "❌ Docker daemon ไม่ทำงาน" "Error"
            Write-ColorText "💡 เริ่มต้น Docker Desktop" "Info"
            return $false
        }
    } catch {
        Write-ColorText "❌ ไม่สามารถเชื่อมต่อ Docker daemon" "Error"
        return $false
    }
    
    # Check if docker-compose is available
    try {
        $composeVersion = docker-compose --version 2>&1
        if ($composeVersion -match "docker-compose version") {
            Write-ColorText "✅ Docker Compose: $composeVersion" "Success"
        } else {
            Write-ColorText "⚠️  Docker Compose ไม่พบ - ใช้ docker compose แทน" "Warning"
        }
    } catch {
        Write-ColorText "⚠️  Docker Compose ไม่พบ" "Warning"
    }
    
    Write-Host ""
    return $true
}

function Build-DockerImage {
    Write-ColorText "🔨 สร้าง Docker Image..." "Info"
    
    try {
        docker build -t universal-fs-mcp:latest .
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ สร้าง Docker Image สำเร็จ" "Success"
        } else {
            Write-ColorText "❌ สร้าง Docker Image ล้มเหลว" "Error"
            return $false
        }
    } catch {
        Write-ColorText "❌ เกิดข้อผิดพลาดในการสร้าง Docker Image: $($_.Exception.Message)" "Error"
        return $false
    }
    
    return $true
}

function Start-DockerContainer {
    Write-ColorText "🚀 เริ่มต้น Docker Container..." "Info"
    
    try {
        if ($Mode -eq "prod") {
            Write-ColorText "📦 โหมด Production" "Info"
            docker-compose up -d --build
        } else {
            Write-ColorText "🔧 โหมด Development" "Info"
            docker-compose up --build
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ เริ่มต้น Container สำเร็จ" "Success"
        } else {
            Write-ColorText "❌ เริ่มต้น Container ล้มเหลว" "Error"
            return $false
        }
    } catch {
        Write-ColorText "❌ เกิดข้อผิดพลาดในการเริ่มต้น Container: $($_.Exception.Message)" "Error"
        return $false
    }
    
    return $true
}

function Stop-DockerContainer {
    Write-ColorText "🛑 หยุด Docker Container..." "Info"
    
    try {
        docker-compose down
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ หยุด Container สำเร็จ" "Success"
        } else {
            Write-ColorText "❌ หยุด Container ล้มเหลว" "Error"
            return $false
        }
    } catch {
        Write-ColorText "❌ เกิดข้อผิดพลาดในการหยุด Container: $($_.Exception.Message)" "Error"
        return $false
    }
    
    return $true
}

function Show-DockerLogs {
    Write-ColorText "📋 แสดง Docker Logs..." "Info"
    
    try {
        docker-compose logs -f universal-mcp-server
    } catch {
        Write-ColorText "❌ เกิดข้อผิดพลาดในการแสดง logs: $($_.Exception.Message)" "Error"
    }
}

function Enter-DockerShell {
    Write-ColorText "🐚 เข้าไปใน Docker Container..." "Info"
    
    try {
        docker exec -it universal-fs-mcp-server /bin/bash
    } catch {
        Write-ColorText "❌ เกิดข้อผิดพลาดในการเข้า Container: $($_.Exception.Message)" "Error"
    }
}

function Show-DockerStatus {
    Write-ColorText "📊 สถานะ Docker Containers..." "Info"
    
    try {
        docker-compose ps
        Write-Host ""
        docker stats --no-stream
    } catch {
        Write-ColorText "❌ เกิดข้อผิดพลาดในการแสดงสถานะ: $($_.Exception.Message)" "Error"
    }
}

function Clean-DockerResources {
    Write-ColorText "🧹 ทำความสะอาด Docker Resources..." "Info"
    
    try {
        # Stop and remove containers
        docker-compose down --volumes --remove-orphans
        
        # Remove images
        docker rmi universal-fs-mcp:latest -f
        
        # Remove unused resources
        docker system prune -f
        
        Write-ColorText "✅ ทำความสะอาดสำเร็จ" "Success"
    } catch {
        Write-ColorText "❌ เกิดข้อผิดพลาดในการทำความสะอาด: $($_.Exception.Message)" "Error"
    }
}

function Show-Help {
    Show-Header
    
    Write-ColorText "📖 ตัวอย่างการใช้งาน:" "SubHeader"
    Write-ColorText "   .\start-docker.ps1 -Action build              # สร้าง Docker Image" "Info"
    Write-ColorText "   .\start-docker.ps1 -Action start              # เริ่มต้น Container (dev)" "Info"
    Write-ColorText "   .\start-docker.ps1 -Action start -Mode prod   # เริ่มต้น Container (prod)" "Info"
    Write-ColorText "   .\start-docker.ps1 -Action stop               # หยุด Container" "Info"
    Write-ColorText "   .\start-docker.ps1 -Action restart            # รีสตาร์ท Container" "Info"
    Write-ColorText "   .\start-docker.ps1 -Action logs               # แสดง Logs" "Info"
    Write-ColorText "   .\start-docker.ps1 -Action shell              # เข้าไปใน Container" "Info"
    Write-ColorText "   .\start-docker.ps1 -Action status             # แสดงสถานะ" "Info"
    Write-ColorText "   .\start-docker.ps1 -Action clean              # ทำความสะอาด" "Info"
    
    Write-Host ""
    Write-ColorText "🔗 Documentation:" "SubHeader"
    Write-ColorText "   📄 Dockerfile" "Info"
    Write-ColorText "   📄 docker-compose.yml" "Info"
    
    Write-Host ""
    Write-ColorText "🌐 Features:" "SubHeader"
    Write-ColorText "   • Containerized MCP Server" "Info"
    Write-ColorText "   • Cross-platform Compatibility" "Info"
    Write-ColorText "   • Resource Management" "Info"
    Write-ColorText "   • Health Monitoring" "Info"
    Write-ColorText "   • Data Persistence" "Info"
}

# Main execution
Show-Header

if (-not (Test-DockerPrerequisites)) {
    Write-ColorText "❌ Docker Prerequisites ไม่ครบถ้วน" "Error"
    exit 1
}

switch ($Action) {
    "build" {
        Build-DockerImage
    }
    "start" {
        Start-DockerContainer
    }
    "stop" {
        Stop-DockerContainer
    }
    "restart" {
        Stop-DockerContainer
        Start-DockerContainer
    }
    "logs" {
        Show-DockerLogs
    }
    "shell" {
        Enter-DockerShell
    }
    "status" {
        Show-DockerStatus
    }
    "clean" {
        Clean-DockerResources
    }
    default {
        Write-ColorText "❌ การกระทำไม่ถูกต้อง: $Action" "Error"
        Show-Help
        exit 1
    }
}

Write-Host ""
Write-ColorText "✨ Docker Universal File System MCP Server - Complete!" "Success"

