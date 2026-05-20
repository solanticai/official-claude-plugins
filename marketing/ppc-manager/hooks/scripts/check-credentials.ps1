# ppc-manager SessionStart hook — PowerShell sibling of check-credentials.sh.

$ErrorActionPreference = 'Continue'

$pluginRoot = $env:CLAUDE_PLUGIN_ROOT
if (-not $pluginRoot) { $pluginRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }

$dataDir = $env:CLAUDE_PLUGIN_DATA
if (-not $dataDir) { $dataDir = Join-Path $env:USERPROFILE '.claude\plugins\data\ppc-manager' }

$pyPathFile = Join-Path $dataDir 'python_path.txt'
if (-not (Test-Path $pyPathFile)) { exit 0 }
$py = (Get-Content $pyPathFile -Raw).Trim()
if (-not (Test-Path $py)) { exit 0 }

$passphrase = $env:CLAUDE_PLUGIN_OPTION_PPC_VAULT_PASSPHRASE
$vaultPath = $env:PPC_VAULT_PATH
if (-not $vaultPath) { $vaultPath = Join-Path $dataDir 'tokens.enc' }

if (-not $passphrase) {
  Write-Output '{"systemMessage":"ppc-manager: vault passphrase not set. Configure ppc_vault_passphrase in plugin settings."}'
  exit 0
}

if (-not (Test-Path $vaultPath)) {
  Write-Output '{"systemMessage":"ppc-manager: credential vault not found. Run /ppc-manager:oauth-setup to connect Google and Meta."}'
  exit 0
}

$env:PPC_VAULT_PATH = $vaultPath
$env:PPC_VAULT_PASSPHRASE = $passphrase

$script = Join-Path $pluginRoot 'scripts\token_validator.py'
$output = & $py $script --quiet --json 2>&1
$ec = $LASTEXITCODE

if ($ec -eq 0) { exit 0 }

$msg = "ppc-manager: credential check failed. Run /ppc-manager:oauth-setup refresh."
Write-Output "{`"systemMessage`":`"$msg`"}"
exit 0
