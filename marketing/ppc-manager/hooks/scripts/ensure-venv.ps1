# ppc-manager SessionStart hook — PowerShell sibling of ensure-venv.sh.
# Creates or updates ${CLAUDE_PLUGIN_DATA}/venv from requirements.txt.

$ErrorActionPreference = 'Continue'

$pluginRoot = $env:CLAUDE_PLUGIN_ROOT
if (-not $pluginRoot) { $pluginRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }

$dataDir = $env:CLAUDE_PLUGIN_DATA
if (-not $dataDir) { $dataDir = Join-Path $env:USERPROFILE '.claude\plugins\data\ppc-manager' }

$venv = Join-Path $dataDir 'venv'
$req  = Join-Path $pluginRoot 'requirements.txt'
$stamp = Join-Path $dataDir 'requirements.stamp'
$log  = Join-Path $dataDir 'install.log'

New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

# Pick a Python interpreter
$py = $env:PPC_PYTHON
if (-not $py) {
  if (Get-Command python -ErrorAction SilentlyContinue) { $py = 'python' }
  elseif (Get-Command py -ErrorAction SilentlyContinue) { $py = 'py -3' }
  else {
    Write-Output '{"systemMessage":"ppc-manager: Python 3.11+ not found on PATH. Install it and restart Claude Code."}'
    exit 0
  }
}

# Version check
$versionOk = & $py -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Output '{"systemMessage":"ppc-manager: Python 3.11+ required. MCP servers will not start."}'
  exit 0
}

if (-not (Test-Path $venv)) {
  & $py -m venv $venv 2>&1 | Out-File -FilePath $log -Append
  if ($LASTEXITCODE -ne 0) {
    Write-Output "{`"systemMessage`":`"ppc-manager: venv creation failed. See $log.`"}"
    exit 0
  }
}

$pipPath = Join-Path $venv 'Scripts\pip.exe'
$vpyPath = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $pipPath)) {
  $pipPath = Join-Path $venv 'bin/pip'
  $vpyPath = Join-Path $venv 'bin/python'
}
if (-not (Test-Path $pipPath)) {
  Write-Output "{`"systemMessage`":`"ppc-manager: venv pip not found inside $venv.`"}"
  exit 0
}

Set-Content -Path (Join-Path $dataDir 'python_path.txt') -Value $vpyPath

$needsInstall = $true
if (Test-Path $stamp) {
  $reqHash = (Get-FileHash $req).Hash
  $stampHash = (Get-FileHash $stamp).Hash
  if ($reqHash -eq $stampHash) { $needsInstall = $false }
}

if ($needsInstall) {
  & $pipPath install --upgrade pip 2>&1 | Out-File -FilePath $log -Append
  & $pipPath install -r $req 2>&1 | Out-File -FilePath $log -Append
  if ($LASTEXITCODE -ne 0) {
    Write-Output "{`"systemMessage`":`"ppc-manager: pip install failed. See $log for details.`"}"
    exit 0
  }
  Copy-Item -Force $req $stamp
}

exit 0
