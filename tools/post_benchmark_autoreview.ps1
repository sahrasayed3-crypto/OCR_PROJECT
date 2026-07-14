param(
    [string]$WorkspaceRoot = (Get-Location).Path,
    [int]$PollSeconds = 30
)

$ErrorActionPreference = "Stop"

function Get-BenchmarkProcesses {
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -like "python*" -and
            $_.CommandLine -match "tools/run_full_benchmark.py"
        }
}

function Write-Line {
    param([string]$Path, [string]$Text)
    Add-Content -LiteralPath $Path -Value $Text -Encoding UTF8
}

Set-Location -LiteralPath $WorkspaceRoot

$logsDir = Join-Path $WorkspaceRoot "logs"
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$progressLog = Join-Path $logsDir "post_benchmark_autoreview_$stamp.log"
$summaryMd = Join-Path $logsDir "post_benchmark_summary_$stamp.md"

Write-Line $progressLog "[$(Get-Date -Format s)] watcher started"
Write-Line $progressLog "[$(Get-Date -Format s)] waiting for benchmark processes to finish..."

while ($true) {
    $procs = @(Get-BenchmarkProcesses)
    if ($procs.Count -eq 0) {
        break
    }
    Write-Line $progressLog "[$(Get-Date -Format s)] still running: $($procs.ProcessId -join ',')"
    Start-Sleep -Seconds $PollSeconds
}

Write-Line $progressLog "[$(Get-Date -Format s)] benchmark processes finished, starting review"

$latestJson = Get-ChildItem -LiteralPath (Join-Path $WorkspaceRoot "samples/generated") -Filter "benchmark_report_*.json" -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
$latestMd = Get-ChildItem -LiteralPath (Join-Path $WorkspaceRoot "samples/generated") -Filter "benchmark_report_*.md" -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

$benchSummary = $null
if ($latestJson) {
    $benchSummary = Get-Content -LiteralPath $latestJson.FullName -Encoding UTF8 | ConvertFrom-Json
}

$allFiles = @(Get-ChildItem -LiteralPath $WorkspaceRoot -Recurse -File)
$pyFiles = @($allFiles | Where-Object { $_.Extension -eq ".py" })
$compileTargets = @(
    "app.py",
    "pdfword",
    "scripts",
    "tests"
)
$compileTargets += @(Get-ChildItem -LiteralPath (Join-Path $WorkspaceRoot "tools") -Filter "*.py" -File |
    ForEach-Object { $_.FullName })

$unitOut = & python -m unittest discover -s tests 2>&1 | Out-String
$unitCode = $LASTEXITCODE

$compileOut = & python -m compileall -q @compileTargets 2>&1 | Out-String
$compileCode = $LASTEXITCODE

$rgExcludes = @(
    "--glob", "!tools/python/**",
    "--glob", "!tools/poppler/**",
    "--glob", "!poppler-26.02.0/**",
    "--glob", "!.venv*/**",
    "--glob", "!data/**",
    "--glob", "!conversions/**",
    "--glob", "!logs/**",
    "--glob", "!outputs/**",
    "--glob", "!backups/**"
)
$todoHits = & rg -n @rgExcludes "TODO|FIXME|XXX|HACK" . 2>$null | Out-String
$bareExceptHits = & rg -n @rgExcludes "except\s*:" . 2>$null | Out-String

$nowIso = (Get-Date).ToString("s")
$report = @()
$report += "# Post-Benchmark Autonomous Review"
$report += ""
$report += "- Generated at: $nowIso"
$report += "- Workspace: `$WorkspaceRoot`"
$report += ""

if ($latestJson) {
    $report += "## Benchmark Final Result"
    $report += ""
    $report += "- Latest JSON report: `$($latestJson.FullName)`"
    if ($latestMd) {
        $report += "- Latest Markdown report: `$($latestMd.FullName)`"
    }
    if ($benchSummary) {
        $report += "- Total cases: $($benchSummary.summary.total_cases)"
        $report += "- Success: $($benchSummary.summary.success_cases)"
        $report += "- Expected failures passed: $($benchSummary.summary.expected_failures_ok)"
        $report += "- Failed: $($benchSummary.summary.failed_cases)"
        $report += "- Avg word accuracy: $($benchSummary.summary.avg_word_accuracy)"
        $report += "- Avg char accuracy: $($benchSummary.summary.avg_char_accuracy)"
    }
    $report += ""
}

$report += "## Project Review Snapshot"
$report += ""
$report += "- Total files scanned: $($allFiles.Count)"
$report += "- Python files scanned: $($pyFiles.Count)"
$report += "- Unit tests exit code: $unitCode"
$report += "- Compile-all exit code: $compileCode"
$report += ""

$report += "### Unit Test Output"
$report += ""
$report += "```text"
$report += ($unitOut.Trim())
$report += "```"
$report += ""

$report += "### Compile Output"
$report += ""
$report += "```text"
$report += ($compileOut.Trim())
$report += "```"
$report += ""

$report += "### Potential Improvement Signals"
$report += ""
$report += "#### TODO/FIXME/HACK hits"
$report += ""
$report += "```text"
$report += ($(if ([string]::IsNullOrWhiteSpace($todoHits)) { "No hits." } else { $todoHits.Trim() }))
$report += "```"
$report += ""
$report += "#### Bare except hits"
$report += ""
$report += "```text"
$report += ($(if ([string]::IsNullOrWhiteSpace($bareExceptHits)) { "No hits." } else { $bareExceptHits.Trim() }))
$report += "```"
$report += ""

$report += "## Suggested Next Improvements"
$report += ""
$report += "1. Prioritize failures in latest benchmark report and add targeted regression tests."
$report += "2. Replace bare `except:` blocks with explicit exception classes where possible."
$report += "3. Resolve high-priority TODO/FIXME markers in benchmark/ocr critical paths."
$report += "4. Re-run full benchmark after each major OCR pipeline change to keep trend history stable."

$reportText = $report -join "`r`n"
Set-Content -LiteralPath $summaryMd -Value $reportText -Encoding UTF8

Write-Line $progressLog "[$(Get-Date -Format s)] review completed"
Write-Line $progressLog "[$(Get-Date -Format s)] summary: $summaryMd"
