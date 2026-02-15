# Xiaohongshu Crawler V4.0 Launcher
# PowerShell启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Xiaohongshu Crawler V4.0" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    python crawler_v4.py
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
