# Xiaohongshu Crawler V3.0 Launcher

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Xiaohongshu Crawler V3.0" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/3] Checking Python..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "      $pythonVersion" -ForegroundColor White
} else {
    Write-Host "      Error: Python not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check dependencies
Write-Host "[2/3] Checking dependencies..." -ForegroundColor Green
try {
    $result = pip show playwright 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      playwright installed" -ForegroundColor White
    }
} catch {
    Write-Host "      Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Install browser
Write-Host "[3/3] Installing browser..." -ForegroundColor Green
try {
    python -m playwright install chromium
} catch {
    Write-Host "      Warning: Browser installation failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting crawler..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run crawler
python crawler_v3.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
