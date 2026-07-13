$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$python = Join-Path $root '.venv311\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $python = 'python'
}

$logs = Join-Path $root 'logs'
New-Item -ItemType Directory -Force -Path $logs | Out-Null

$poppler = Join-Path $root 'tools\poppler\Library\bin'
if (Test-Path -LiteralPath $poppler -PathType Container) {
    $env:PATH = "$poppler;$env:PATH"
}

$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:APP_ROLE = if ($env:APP_ROLE) { $env:APP_ROLE } else { 'server' }
$env:SERVER_BASE_URL = if ($env:SERVER_BASE_URL) { $env:SERVER_BASE_URL } else { 'http://127.0.0.1:8000' }
$env:LOCAL_PROCESSING_ENABLED = if ($env:LOCAL_PROCESSING_ENABLED) { $env:LOCAL_PROCESSING_ENABLED } else { 'true' }

$apiOut = Join-Path $logs 'api.out.log'
$apiErr = Join-Path $logs 'api.err.log'
$uiOut = Join-Path $logs 'streamlit.out.log'
$uiErr = Join-Path $logs 'streamlit.err.log'

Start-Process -FilePath $python `
    -ArgumentList @('-m', 'uvicorn', 'pdfword.worker_api:app', '--host', '127.0.0.1', '--port', '8000') `
    -WorkingDirectory $root `
    -RedirectStandardOutput $apiOut `
    -RedirectStandardError $apiErr `
    -WindowStyle Hidden

Start-Sleep -Seconds 2

Start-Process -FilePath $python `
    -ArgumentList @('-m', 'streamlit', 'run', 'app.py', '--server.address', '127.0.0.1', '--server.port', '8501', '--server.headless', 'true', '--server.fileWatcherType', 'none') `
    -WorkingDirectory $root `
    -RedirectStandardOutput $uiOut `
    -RedirectStandardError $uiErr `
    -WindowStyle Hidden

Write-Host 'Clouda PDF started.'
Write-Host 'UI:  http://127.0.0.1:8501'
Write-Host 'API: http://127.0.0.1:8000/health'
