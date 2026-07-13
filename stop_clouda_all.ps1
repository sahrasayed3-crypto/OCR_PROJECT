$ErrorActionPreference = 'Stop'

$pidFile = Join-Path $PSScriptRoot 'logs\clouda-processes.json'
if (-not (Test-Path -LiteralPath $pidFile -PathType Leaf)) {
    Write-Output 'No Clouda process file exists; nothing to stop.'
    exit 0
}

$records = Get-Content -Raw -LiteralPath $pidFile | ConvertFrom-Json
foreach ($record in $records) {
    $process = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
    if (-not $process) {
        continue
    }
    $actual = $process.StartTime.ToUniversalTime().ToString('o')
    if ($actual -ne $record.started) {
        Write-Warning "PID $($record.pid) was reused; it was not stopped."
        continue
    }
    Stop-Process -Id $record.pid
    Wait-Process -Id $record.pid -Timeout 15 -ErrorAction SilentlyContinue
    Write-Output "Stopped Clouda $($record.name) (PID $($record.pid))."
}

Move-Item -LiteralPath $pidFile -Destination "$pidFile.stopped-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
