#!/usr/bin/env powershell
<#
.SYNOPSIS
    Launches the Unified File System MCP Chat App.
.DESCRIPTION
    This script launches the main, unified chat application.
#>

Write-Host "🚀 Launching Unified File System MCP Chat App..." -ForegroundColor Cyan

$AppPath = "apps/unified_chat_app.py"

# Check if the application file exists
if (-not (Test-Path $AppPath)) {
    Write-Host "❌ ERROR: Application file not found at '$AppPath'" -ForegroundColor Red
    Write-Host "Please ensure the repository structure is correct."
    pause
    exit 1
}

# Check for a virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "📦 Activating Virtual Environment..." -ForegroundColor Green
    & venv\Scripts\Activate.ps1
    python $AppPath
} else {
    Write-Host "🌐 Using global Python environment." -ForegroundColor Yellow
    python $AppPath
}

Write-Host "✅ Application finished." -ForegroundColor Green
