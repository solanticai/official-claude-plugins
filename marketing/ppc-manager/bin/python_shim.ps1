# Resolve the Python interpreter written by ensure-venv.ps1 and exec it.
# Used on Windows by .mcp.json for native PowerShell hosts.

$dataDir = $env:CLAUDE_PLUGIN_DATA
if (-not $dataDir) { $dataDir = Join-Path $env:USERPROFILE '.claude\plugins\data\ppc-manager' }

$pyPathFile = Join-Path $dataDir 'python_path.txt'
if (-not (Test-Path $pyPathFile)) {
  Write-Error "ppc-manager: python_path.txt not found; did ensure-venv run?"
  exit 127
}

$py = (Get-Content $pyPathFile -Raw).Trim()
if (-not (Test-Path $py)) {
  Write-Error "ppc-manager: interpreter at $py is missing"
  exit 127
}

& $py @args
exit $LASTEXITCODE
