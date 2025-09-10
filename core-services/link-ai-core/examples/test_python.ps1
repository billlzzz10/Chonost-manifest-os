#!/usr/bin/env pwsh

Write-Host "🔍 ทดสอบหา Python ในระบบ..." -ForegroundColor Cyan

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
        Write-Host "   ทดสอบ: $pythonPath" -ForegroundColor Yellow
        
        if ($pythonPath -eq "python" -or $pythonPath -eq "py" -or $pythonPath -eq "python3") {
            $pythonVersion = & $pythonPath --version 2>&1
        } else {
            if (Test-Path $pythonPath) {
                $pythonVersion = & $pythonPath --version 2>&1
            } else {
                Write-Host "     ❌ ไม่พบไฟล์" -ForegroundColor Red
                continue
            }
        }
        
        if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
            $version = $matches[1]
            Write-Host "     ✅ พบ Python: $version" -ForegroundColor Green
            $script:PythonExecutable = $pythonPath
            $pythonFound = $true
            break
        } else {
            Write-Host "     ❌ ไม่ใช่ Python ที่ถูกต้อง" -ForegroundColor Red
        }
    } catch {
        Write-Host "     ❌ เกิดข้อผิดพลาด" -ForegroundColor Red
        continue
    }
}

if ($pythonFound) {
    Write-Host "`n🎉 พบ Python แล้ว: $script:PythonExecutable" -ForegroundColor Green
    
    # Test basic modules
    Write-Host "`n🧪 ทดสอบ modules พื้นฐาน..." -ForegroundColor Cyan
    $modules = @("asyncio", "requests", "pathlib")
    foreach ($module in $modules) {
        try {
            & $script:PythonExecutable -c "import $module; print('OK')" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ $module" -ForegroundColor Green
            } else {
                Write-Host "   ❌ $module" -ForegroundColor Red
            }
        } catch {
            Write-Host "   ❌ $module" -ForegroundColor Red
        }
    }
} else {
    Write-Host "`n❌ ไม่พบ Python ในระบบ" -ForegroundColor Red
    Write-Host "💡 ลองติดตั้ง Python จาก https://python.org" -ForegroundColor Yellow
}

