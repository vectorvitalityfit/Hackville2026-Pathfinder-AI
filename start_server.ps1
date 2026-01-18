$ErrorActionPreference = "Stop"

$venvPath = ".\venv"

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venvPath
} else {
    Write-Host "Virtual environment found."
}

Write-Host "Installing dependencies..."
& "$venvPath\Scripts\pip" install -r requirements.txt

Write-Host "Starting Uvicorn..."
& "$venvPath\Scripts\uvicorn" main:app --reload
