# IntraMind Integration Tests - Setup Script
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " IntraMind Integration Tests Setup  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonCheck = Get-Command py -ErrorAction SilentlyContinue
if (-not $pythonCheck) {
    Write-Host "Python not found!" -ForegroundColor Red
    exit 1
}
Write-Host "Found: $(py --version)" -ForegroundColor Green

# Check for existing venv
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
    $response = Read-Host "Recreate it? (y/N)"
    if ($response -eq "y") {
        Remove-Item -Recurse -Force "venv"
    } else {
        Write-Host "Using existing venv." -ForegroundColor Green
        exit 0
    }
}

# Create venv
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
py -m venv venv
if (Test-Path "venv") {
    Write-Host "Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "Failed to create venv" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
.\venv\Scripts\python.exe -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\pip.exe install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Done
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Activate venv:  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Run tests:      pytest integration/ -v" -ForegroundColor White
Write-Host ""
