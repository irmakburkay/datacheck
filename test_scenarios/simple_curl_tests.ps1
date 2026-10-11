# Simple PowerShell test script for DataCheck API
# Tests endpoints using Invoke-WebRequest (built-in)

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     DataCheck API Test Suite (PowerShell)                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$BaseUrl = "http://127.0.0.1:5000"
$PassCount = 0
$TotalTests = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [int]$ExpectedStatus = 200
    )
    
    $script:TotalTests++
    
    Write-Host "`n============================================================" -ForegroundColor Blue
    Write-Host "  TEST: $Name" -ForegroundColor Blue
    Write-Host "============================================================" -ForegroundColor Blue
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params -ErrorAction Stop
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "✓ PASS - HTTP $($response.StatusCode)" -ForegroundColor Green
            $script:PassCount++
            
            # Show content for JSON responses
            if ($response.Content -match '^\s*\{') {
                try {
                    $json = $response.Content | ConvertFrom-Json
                    Write-Host "→ Response:" -ForegroundColor Yellow
                    Write-Host ($json | ConvertTo-Json -Depth 3) -ForegroundColor Gray
                } catch {
                    Write-Host "→ Response: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))" -ForegroundColor Gray
                }
            }
            
            return $true
        } else {
            Write-Host "✗ FAIL - Expected $ExpectedStatus, got $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq $ExpectedStatus) {
            Write-Host "✓ PASS - HTTP $statusCode (expected error)" -ForegroundColor Green
            $script:PassCount++
            return $true
        } else {
            Write-Host "✗ FAIL - $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    }
}

# Test 1: Health endpoint
Test-Endpoint -Name "Health Endpoint" -Url "$BaseUrl/health"

# Test 2: Index page
$result = Test-Endpoint -Name "Index Page" -Url "$BaseUrl/"
if ($result) {
    Write-Host "→ Index page loaded successfully" -ForegroundColor Yellow
}

# Test 3: Sample CSV download
Test-Endpoint -Name "Sample CSV Download" -Url "$BaseUrl/sample-csv"

# Test 4: 404 Handler
Test-Endpoint -Name "404 Error Handler" -Url "$BaseUrl/this-does-not-exist" -ExpectedStatus 404

# Test 5: CSV Upload (using multipart form data)
Write-Host "`n============================================================" -ForegroundColor Blue
Write-Host "  TEST: CSV File Upload" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue

$script:TotalTests++

try {
    # Create a simple CSV file
    $csvPath = "$PSScriptRoot\scenario1_numeric.csv"
    
    if (Test-Path $csvPath) {
        # Build multipart form data manually
        $boundary = [System.Guid]::NewGuid().ToString()
        $LF = "`r`n"
        
        $csvContent = Get-Content $csvPath -Raw
        
        $bodyLines = @(
            "--$boundary",
            "Content-Disposition: form-data; name=`"name`"",
            "",
            "Test User",
            "--$boundary",
            "Content-Disposition: form-data; name=`"email`"",
            "",
            "test@example.com",
            "--$boundary",
            "Content-Disposition: form-data; name=`"service`"",
            "",
            "Basic CSV Analysis",
            "--$boundary",
            "Content-Disposition: form-data; name=`"description`"",
            "",
            "PowerShell API Test",
            "--$boundary",
            "Content-Disposition: form-data; name=`"csv_file`"; filename=`"test.csv`"",
            "Content-Type: text/csv",
            "",
            $csvContent,
            "--$boundary--"
        )
        
        $body = $bodyLines -join $LF
        
        $response = Invoke-WebRequest -Uri "$BaseUrl/api/analyze" `
            -Method POST `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $body `
            -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ PASS - CSV uploaded and analyzed" -ForegroundColor Green
            $script:PassCount++
            
            $result = $response.Content | ConvertFrom-Json
            Write-Host "→ Request ID: $($result.request_id)" -ForegroundColor Yellow
            Write-Host "→ Total rows: $($result.analysis.total_rows)" -ForegroundColor Yellow
            Write-Host "→ Total columns: $($result.analysis.total_columns)" -ForegroundColor Yellow
            Write-Host "→ Duplicate rows: $($result.analysis.duplicate_rows)" -ForegroundColor Yellow
            
            # Check for new features
            $firstCol = $result.analysis.columns[0]
            if ($firstCol.unique_count) {
                Write-Host "→ ✓ Unique counts feature detected" -ForegroundColor Green
            }
            if ($firstCol.stats) {
                Write-Host "→ ✓ Statistical metrics feature detected" -ForegroundColor Green
                Write-Host "    Min: $($firstCol.stats.min), Max: $($firstCol.stats.max)" -ForegroundColor Gray
            }
            
            # Test download
            Write-Host "`n→ Testing download endpoint..." -ForegroundColor Yellow
            $downloadUrl = "$BaseUrl$($result.download_url)"
            $dlResponse = Invoke-WebRequest -Uri $downloadUrl -UseBasicParsing
            if ($dlResponse.StatusCode -eq 200) {
                Write-Host "  ✓ Download works" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "✗ FAIL - Test CSV file not found: $csvPath" -ForegroundColor Red
    }
}
catch {
    Write-Host "✗ FAIL - $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n============================================================" -ForegroundColor Blue
Write-Host "  TEST SUMMARY" -ForegroundColor Blue
Write-Host "============================================================" -ForegroundColor Blue

$percentage = if ($TotalTests -gt 0) { ($PassCount / $TotalTests * 100) } else { 0 }
$color = if ($percentage -eq 100) { "Green" } elseif ($percentage -ge 80) { "Yellow" } else { "Red" }

Write-Host "`nResult: $PassCount/$TotalTests tests passed ($([Math]::Round($percentage, 1))%)" -ForegroundColor $color
Write-Host "============================================================`n" -ForegroundColor Blue

exit $(if ($PassCount -eq $TotalTests) { 0 } else { 1 })
