# Starts GPT Researcher (uvicorn) in the background. :-)
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$LogsDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogsDir "startup.log"

Set-Location $ProjectRoot

if (-not (Test-Path $Python)) {
    throw "Python venv not found at $Python"
}

if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

$alreadyListening = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($alreadyListening) {
    Add-Content -Path $LogFile -Value "$(Get-Date -Format o) Port 8000 already in use; skipping start."
    exit 0
}

Add-Content -Path $LogFile -Value "$(Get-Date -Format o) Starting GPT Researcher server..."

& $Python -m uvicorn main:app --host 127.0.0.1 --port 8000 *>> $LogFile
