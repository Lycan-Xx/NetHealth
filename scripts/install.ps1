# NetHealth PowerShell installation script

Write-Host "Installing NetHealth..." -ForegroundColor Green

# Check Python version
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python 3 is required but not installed." -ForegroundColor Red
    exit 1
}

# Check pip
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "Error: pip is required but not installed." -ForegroundColor Red
    exit 1
}

# Install poetry if not present
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Poetry..." -ForegroundColor Yellow
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
poetry install

# Create symlink
Write-Host "Creating command symlink..." -ForegroundColor Yellow
poetry run pip install --editable .

Write-Host "NetHealth installation complete!" -ForegroundColor Green
Write-Host "Run 'nethealth --help' to get started." -ForegroundColor Cyan