$ErrorActionPreference = 'Stop'

$logDir = Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$poppler = Join-Path $PSScriptRoot 'tools\poppler\Library\bin'
if (Test-Path -LiteralPath $poppler -PathType Container) {
    $env:PATH = "$poppler;$env:PATH"
}

$stdout = Join-Path $logDir 'streamlit.out.log'
$stderr = Join-Path $logDir 'streamlit.err.log'
$port = $null
foreach ($candidate in 8501, 8502) {
    try {
        $test = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $candidate)
        $test.Start()
        $test.Stop()
        $port = $candidate
        break
    }
    catch {
        continue
    }
}
if (-not $port) {
    throw 'No available Streamlit port found.'
}

$python = Join-Path $PSScriptRoot '.venv311\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    $python = 'python'
}

Start-Process -FilePath $python `
    -ArgumentList @('-m', 'streamlit', 'run', 'app.py', '--server.address', '127.0.0.1', '--server.port', "$port") `
    -WorkingDirectory $PSScriptRoot `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -WindowStyle Hidden

Write-Host "Clouda PDF started at http://127.0.0.1:$port"
