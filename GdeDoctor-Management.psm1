# GdeDoctor Project Management Scripts for Windows PowerShell

# Function to install dependencies
function Install-Dependencies {
    Write-Host "Installing GdeDoctor project dependencies..." -ForegroundColor Green
    
    Write-Host "`nInstalling backend dependencies..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv .venv
    & .venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Set-Location ..
    
    Write-Host "`nInstalling bot dependencies..." -ForegroundColor Yellow
    Set-Location bot
    python -m venv .venv
    & .venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Set-Location ..
    
    Write-Host "`n✓ All dependencies installed successfully!" -ForegroundColor Green
}

# Function to start backend
function Start-Backend {
    Write-Host "Starting GdeDoctor Backend..." -ForegroundColor Green
    Set-Location backend
    & .venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Function to start bot
function Start-Bot {
    Write-Host "Starting GdeDoctor Bot..." -ForegroundColor Green
    Set-Location bot
    & .venv\Scripts\Activate.ps1
    python -m app.main
}

# Function to start both services
function Start-Dev {
    Write-Host "Starting GdeDoctor Development Environment..." -ForegroundColor Green
    Write-Host "Backend will run on http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Bot will start after backend is ready" -ForegroundColor Cyan
    
    # Start backend in background
    Start-Process powershell -ArgumentList "-Command", "cd '$PWD\backend'; & .venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal
    
    # Wait for backend to start
    Start-Sleep -Seconds 5
    
    # Start bot in background
    Start-Process powershell -ArgumentList "-Command", "cd '$PWD\bot'; & .venv\Scripts\Activate.ps1; python -m app.main" -WindowStyle Normal
    
    Write-Host "`nBoth services started in separate windows" -ForegroundColor Green
    Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
}

# Function to stop all services
function Stop-All {
    Write-Host "Stopping all GdeDoctor services..." -ForegroundColor Red
    
    Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process | Where-Object {$_.ProcessName -eq "uvicorn"} | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "✓ All services stopped" -ForegroundColor Green
}

# Function to check service status
function Get-Status {
    Write-Host "GdeDoctor Service Status:" -ForegroundColor Cyan
    
    $backendRunning = Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*uvicorn*"}
    $botRunning = Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*app.main*"}
    
    if ($backendRunning) {
        Write-Host "✓ Backend: Running on http://localhost:8000" -ForegroundColor Green
    } else {
        Write-Host "✗ Backend: Not running" -ForegroundColor Red
    }
    
    if ($botRunning) {
        Write-Host "✓ Bot: Running" -ForegroundColor Green
    } else {
        Write-Host "✗ Bot: Not running" -ForegroundColor Red
    }
}

# Function to show help
function Show-Help {
    Write-Host "GdeDoctor Project Management Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Install-Dependencies  - Install all project dependencies" -ForegroundColor White
    Write-Host "Start-Backend         - Start backend server only" -ForegroundColor White
    Write-Host "Start-Bot            - Start bot only" -ForegroundColor White
    Write-Host "Start-Dev            - Start both backend and bot" -ForegroundColor White
    Write-Host "Stop-All             - Stop all running services" -ForegroundColor White
    Write-Host "Get-Status            - Check service status" -ForegroundColor White
    Write-Host "Show-Help             - Show this help message" -ForegroundColor White
}

# Export functions for use
Export-ModuleMember -Function Install-Dependencies, Start-Backend, Start-Bot, Start-Dev, Stop-All, Get-Status, Show-Help
