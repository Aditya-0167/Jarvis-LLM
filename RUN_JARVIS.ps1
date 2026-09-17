$ErrorActionPreference = "Stop"
if (-not (Test-Path .venv)) { py -3.14 -m venv .venv }
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py init
python main.py bootstrap --steps 60
python main.py benchmark
python main.py status
Write-Host "JARVIS is initialized. Run: python main.py serve" -ForegroundColor Green
