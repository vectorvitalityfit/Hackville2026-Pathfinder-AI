Set-Location $PSScriptRoot
$venvPath = ".\venv"

# 1. Setup Backend
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venvPath
} else {
    Write-Host "Virtual environment found."
}

Write-Host "Installing backend dependencies..."
& "$venvPath\Scripts\pip" install -r requirements.txt

# 2. Setup Frontend
Write-Host "Setting up Frontend..."
Push-Location ..\frontend
Write-Host "Installing frontend dependencies..."
npm install
Write-Host "Building frontend..."
npm run build
Pop-Location

# 3. Start Server
Write-Host "Starting Uvicorn..."
& "$venvPath\Scripts\uvicorn" app.main:app --reload --host 0.0.0.0
