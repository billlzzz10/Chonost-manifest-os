# PowerShell Script for Testing Complete Chonost System
# ทดสอบระบบทั้งหมดที่เสร็จแล้ว

Write-Host "🚀 Starting Complete Chonost System Test" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$testResults = @()

# Function to test file/directory existence
function Test-SystemComponent {
    param(
        [string]$Path,
        [string]$Type,
        [string]$Description
    )
    
    $fullPath = Join-Path $projectRoot $Path
    $exists = Test-Path $fullPath
    
    if ($exists) {
        Write-Host "✅ $Description" -ForegroundColor Green
        $testResults += @{Component = $Description; Status = "PASS"; Path = $Path}
        return $true
    } else {
        Write-Host "❌ $Description" -ForegroundColor Red
        Write-Host "   Missing: $Path" -ForegroundColor Gray
        $testResults += @{Component = $Description; Status = "FAIL"; Path = $Path}
        return $false
    }
}

# Test 1: File Structure
Write-Host "`n🔍 Testing File Structure..." -ForegroundColor Yellow

$fileTests = @(
    @{Path = "services/backend/src/integrated_system.py"; Description = "Backend Integrated System"},
    @{Path = "services/backend/src/integrated_routes.py"; Description = "Backend API Routes"},
    @{Path = "services/ai/core/enhanced_ai_agents.py"; Description = "AI Enhanced Agents"},
    @{Path = "services/ai/core/agent_forecast.py"; Description = "AI Agent Forecast"},
    @{Path = "services/ai/core/context_manager.py"; Description = "AI Context Manager"},
    @{Path = "services/frontend/web/App.tsx"; Description = "Frontend App Component"},
    @{Path = "services/frontend/web/IconSystem.jsx"; Description = "Frontend Icon System"},
    @{Path = "services/frontend/web/MermaidSystem.jsx"; Description = "Frontend Mermaid System"},
    @{Path = "services/database/prisma/schema.prisma"; Description = "Database Prisma Schema"},
    @{Path = "docker-compose.yml"; Description = "Docker Compose Configuration"},
    @{Path = "env.example"; Description = "Environment Variables Example"}
)

$fileResults = @()
foreach ($test in $fileTests) {
    $result = Test-SystemComponent -Path $test.Path -Type "File" -Description $test.Description
    $fileResults += $result
}

# Test 2: Directory Structure
Write-Host "`n📁 Testing Directory Structure..." -ForegroundColor Yellow

$dirTests = @(
    @{Path = "services/backend/src"; Description = "Backend Source Directory"},
    @{Path = "services/ai/core"; Description = "AI Core Directory"},
    @{Path = "services/frontend/web"; Description = "Frontend Web Directory"},
    @{Path = "services/database/prisma"; Description = "Database Prisma Directory"},
    @{Path = "services/testing"; Description = "Testing Directory"}
)

$dirResults = @()
foreach ($test in $dirTests) {
    $result = Test-SystemComponent -Path $test.Path -Type "Directory" -Description $test.Description
    $dirResults += $result
}

# Test 3: Docker Setup
Write-Host "`n🐳 Testing Docker Setup..." -ForegroundColor Yellow

$dockerTests = @(
    @{Path = "services/backend/Dockerfile"; Description = "Backend Dockerfile"},
    @{Path = "services/ai/Dockerfile"; Description = "AI Service Dockerfile"},
    @{Path = "services/frontend/Dockerfile"; Description = "Frontend Dockerfile"},
    @{Path = "services/testing/Dockerfile"; Description = "Testing Dockerfile"}
)

$dockerResults = @()
foreach ($test in $dockerTests) {
    $result = Test-SystemComponent -Path $test.Path -Type "File" -Description $test.Description
    $dockerResults += $result
}

# Test 4: Requirements Files
Write-Host "`n📦 Testing Requirements Files..." -ForegroundColor Yellow

$reqTests = @(
    @{Path = "services/ai/requirements.txt"; Description = "AI Service Requirements"},
    @{Path = "services/testing/requirements.txt"; Description = "Testing Requirements"}
)

$reqResults = @()
foreach ($test in $reqTests) {
    $result = Test-SystemComponent -Path $test.Path -Type "File" -Description $test.Description
    $reqResults += $result
}

# Calculate overall results
$allResults = @($fileResults + $dirResults + $dockerResults + $reqResults)
$totalTests = $allResults.Count
$passedTests = ($allResults | Where-Object { $_ -eq $true }).Count
$failedTests = $totalTests - $passedTests
$successRate = if ($totalTests -gt 0) { ($passedTests / $totalTests) * 100 } else { 0 }

# Summary
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "📊 COMPLETE SYSTEM TEST SUMMARY" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round($successRate, 1))%" -ForegroundColor Yellow

# Category breakdown
Write-Host "`n📋 CATEGORY BREAKDOWN:" -ForegroundColor Green

$filePassed = ($fileResults | Where-Object { $_ -eq $true }).Count
$fileTotal = $fileResults.Count
Write-Host "Files: $filePassed/$fileTotal ($([math]::Round(($filePassed/$fileTotal)*100, 1))%)" -ForegroundColor $(if ($filePassed -eq $fileTotal) { "Green" } else { "Yellow" })

$dirPassed = ($dirResults | Where-Object { $_ -eq $true }).Count
$dirTotal = $dirResults.Count
Write-Host "Directories: $dirPassed/$dirTotal ($([math]::Round(($dirPassed/$dirTotal)*100, 1))%)" -ForegroundColor $(if ($dirPassed -eq $dirTotal) { "Green" } else { "Yellow" })

$dockerPassed = ($dockerResults | Where-Object { $_ -eq $true }).Count
$dockerTotal = $dockerResults.Count
Write-Host "Docker: $dockerPassed/$dockerTotal ($([math]::Round(($dockerPassed/$dockerTotal)*100, 1))%)" -ForegroundColor $(if ($dockerPassed -eq $dockerTotal) { "Green" } else { "Yellow" })

$reqPassed = ($reqResults | Where-Object { $_ -eq $true }).Count
$reqTotal = $reqResults.Count
Write-Host "Requirements: $reqPassed/$reqTotal ($([math]::Round(($reqPassed/$reqTotal)*100, 1))%)" -ForegroundColor $(if ($reqPassed -eq $reqTotal) { "Green" } else { "Yellow" })

# Detailed results
Write-Host "`n📋 DETAILED RESULTS:" -ForegroundColor Green
foreach ($result in $testResults) {
    $status = if ($result.Status -eq "PASS") { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($result.Status -eq "PASS") { "Green" } else { "Red" }
    Write-Host "$status $($result.Component)" -ForegroundColor $color
}

# Final result
if ($passedTests -eq $totalTests) {
    Write-Host "`n🎉 All tests passed! System structure is complete!" -ForegroundColor Green
    Write-Host "🚀 System is ready for use!" -ForegroundColor Green
    
    Write-Host "`n📋 Available API Endpoints:" -ForegroundColor Cyan
    Write-Host "   - Health Check: GET http://localhost:8000/api/integrated/system/health" -ForegroundColor Gray
    Write-Host "   - Manuscripts: GET/POST http://localhost:8000/api/integrated/manuscripts" -ForegroundColor Gray
    Write-Host "   - AI Analysis: POST http://localhost:8000/api/integrated/ai/analyze-characters" -ForegroundColor Gray
    Write-Host "   - Writing Assistant: POST http://localhost:8000/api/integrated/ai/writing-assistant" -ForegroundColor Gray
    Write-Host "   - Analytics: GET http://localhost:8000/api/integrated/analytics/overview" -ForegroundColor Gray
    
    Write-Host "`n💡 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Start backend server: python scripts/start_backend_server.py" -ForegroundColor Gray
    Write-Host "   2. Test API endpoints: .\scripts\test_api_powershell.ps1" -ForegroundColor Gray
    Write-Host "   3. Start Docker services: docker-compose up --build" -ForegroundColor Gray
    
    exit 0
} else {
    Write-Host "`n⚠️  $failedTests test(s) failed!" -ForegroundColor Red
    Write-Host "Please check the missing components above." -ForegroundColor Yellow
    exit 1
}
