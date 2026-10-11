$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
uv run --group dev python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
uv run --group dev tools/smoke_ui.py
if ($LASTEXITCODE -ne 0) { throw 'UI check failed.' }
uv run --group dev python -m PyInstaller --noconfirm --windowed --onedir --name DarknessLiesAhead --add-data 'assets;assets' --add-data 'data;data' --add-data 'vendor;vendor' main.py
if ($LASTEXITCODE -ne 0) { throw 'Packaging failed.' }
Copy-Item -LiteralPath README.md,CREDITS.md -Destination dist/DarknessLiesAhead/
uv run --group dev tools/dependency_licenses.py dist/DarknessLiesAhead/licenses
if ($LASTEXITCODE -ne 0) { throw 'License collection failed.' }
$report = Join-Path $PWD 'dist/packaged-smoke.txt'
$packagedCheck = Start-Process -FilePath (Join-Path $PWD 'dist/DarknessLiesAhead/DarknessLiesAhead.exe') -ArgumentList @('--smoke-test', '--smoke-report', ('"' + $report + '"')) -WindowStyle Hidden -PassThru -Wait
if ($packagedCheck.ExitCode -ne 0) { throw ('Packaged check failed. See ' + $report) }
Get-Content -LiteralPath $report
Compress-Archive -Path dist/DarknessLiesAhead -DestinationPath dist/DarknessLiesAhead-Windows-x64.zip -Force
Write-Output 'Built dist/DarknessLiesAhead-Windows-x64.zip'
