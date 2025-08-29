# PowerShell Script for Testing Chonost API Endpoints
# ทดสอบ API endpoints ที่เสร็จแล้ว

Write-Host "🚀 Starting Chonost API Endpoints Testing" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"
$testResults = @()

# Function to test API endpoint
function Test-APIEndpoint {
    param(
        [string]$Method,
        [string]$Endpoint,
        [string]$TestName,
        [string]$Body = $null
    )
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        $uri = "$baseUrl$Endpoint"
        
        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers
        } else {
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers -Body $Body
        }
        
        Write-Host "✅ PASS $Method $Endpoint" -ForegroundColor Green
        Write-Host "   Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
        $testResults += @{Test = $TestName; Status = "PASS"; Response = $response}
        return $true
    }
    catch {
        Write-Host "❌ FAIL $Method $Endpoint" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        $testResults += @{Test = $TestName; Status = "FAIL"; Error = $_.Exception.Message}
        return $false
    }
}

# Test 1: Health Check
Write-Host "`nTesting: Health Check" -ForegroundColor Yellow
$healthOk = Test-APIEndpoint -Method "GET" -Endpoint "/api/integrated/system/health" -TestName "Health Check"

# Test 2: Create Manuscript
Write-Host "`nTesting: Create Manuscript" -ForegroundColor Yellow
$manuscriptData = @{
    user_id = "test_user_123"
    title = "Test Manuscript"
    content = "This is a test manuscript for API testing."
} | ConvertTo-Json

$createOk = Test-APIEndpoint -Method "POST" -Endpoint "/api/integrated/manuscripts" -TestName "Create Manuscript" -Body $manuscriptData

# Test 3: Get Manuscripts
Write-Host "`nTesting: Get Manuscripts" -ForegroundColor Yellow
$getOk = Test-APIEndpoint -Method "GET" -Endpoint "/api/integrated/manuscripts?user_id=test_user_123" -TestName "Get Manuscripts"

# Test 4: AI Character Analysis
Write-Host "`nTesting: AI Character Analysis" -ForegroundColor Yellow
$characterData = @{
    content = "John is a brave knight who protects the kingdom. Mary is a wise wizard who helps him on his quest."
} | ConvertTo-Json

$characterOk = Test-APIEndpoint -Method "POST" -Endpoint "/api/integrated/ai/analyze-characters" -TestName "AI Character Analysis" -Body $characterData

# Test 5: AI Plot Analysis
Write-Host "`nTesting: AI Plot Analysis" -ForegroundColor Yellow
$plotData = @{
    content = "The story begins with John discovering a mysterious map. He embarks on a journey to find the hidden treasure."
} | ConvertTo-Json

$plotOk = Test-APIEndpoint -Method "POST" -Endpoint "/api/integrated/ai/analyze-plot" -TestName "AI Plot Analysis" -Body $plotData

# Test 6: Writing Assistant
Write-Host "`nTesting: Writing Assistant" -ForegroundColor Yellow
$writingData = @{
    content = "The hero walked into the cave."
    type = "improve"
} | ConvertTo-Json

$writingOk = Test-APIEndpoint -Method "POST" -Endpoint "/api/integrated/ai/writing-assistant" -TestName "Writing Assistant" -Body $writingData

# Test 7: RAG Search
Write-Host "`nTesting: RAG Search" -ForegroundColor Yellow
$ragData = @{
    query = "character relationships"
} | ConvertTo-Json

$ragOk = Test-APIEndpoint -Method "POST" -Endpoint "/api/integrated/ai/rag-search" -TestName "RAG Search" -Body $ragData

# Test 8: Analytics Overview
Write-Host "`nTesting: Analytics Overview" -ForegroundColor Yellow
$analyticsOk = Test-APIEndpoint -Method "GET" -Endpoint "/api/integrated/analytics/overview" -TestName "Analytics Overview"

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "📊 TEST SUMMARY" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

$totalTests = 8
$passedTests = @($healthOk, $createOk, $getOk, $characterOk, $plotOk, $writingOk, $ragOk, $analyticsOk) | Where-Object { $_ -eq $true } | Measure-Object | Select-Object -ExpandProperty Count
$failedTests = $totalTests - $passedTests
$successRate = ($passedTests / $totalTests) * 100

Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round($successRate, 1))%" -ForegroundColor Yellow

# Detailed results
Write-Host "`n📋 DETAILED RESULTS:" -ForegroundColor Green
foreach ($result in $testResults) {
    $status = if ($result.Status -eq "PASS") { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($result.Status -eq "PASS") { "Green" } else { "Red" }
    Write-Host "$status $($result.Test)" -ForegroundColor $color
}

# Final result
if ($passedTests -eq $totalTests) {
    Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️  $failedTests test(s) failed!" -ForegroundColor Red
    exit 1
}
