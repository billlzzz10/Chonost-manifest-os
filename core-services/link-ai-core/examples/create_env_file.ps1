#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Create .env file from env.example
    สร้างไฟล์ .env จาก env.example

.DESCRIPTION
    This script creates a .env file from env.example for easy configuration
    สคริปต์นี้สร้างไฟล์ .env จาก env.example เพื่อการตั้งค่าที่ง่าย

.EXAMPLE
    .\create_env_file.ps1
#>

# Colors for output
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = $Reset
    )
    Write-Host "$Color$Message$Reset"
}

Write-ColorOutput "🔧 Creating .env file from env.example..." $Blue

# Check if env.example exists
if (-not (Test-Path "env.example")) {
    Write-ColorOutput "❌ env.example not found!" $Red
    exit 1
}

# Check if .env already exists
if (Test-Path ".env") {
    Write-ColorOutput "⚠️  .env file already exists!" $Yellow
    $response = Read-Host "Do you want to overwrite it? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-ColorOutput "❌ Operation cancelled." $Red
        exit 1
    }
}

# Copy env.example to .env
try {
    Copy-Item "env.example" ".env"
    Write-ColorOutput "✅ .env file created successfully!" $Green
    Write-ColorOutput "📝 Please edit .env file and set your Notion Integration Token:" $Blue
    Write-ColorOutput "   NOTION_INTEGRATION_TOKEN=ntn_your_actual_token_here" $Yellow
    Write-ColorOutput "`n💡 You can now run the server with:" $Blue
    Write-ColorOutput "   .\scripts\start-notion-mcp-server.ps1" $Green
}
catch {
    Write-ColorOutput "❌ Failed to create .env file: $_" $Red
    exit 1
}
