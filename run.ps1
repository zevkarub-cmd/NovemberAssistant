Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Stop-Process -Name py -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

$env:PYTHONIOENCODING = "utf-8"

if (Test-Path ".\.venv\Scripts\python.exe") {
    .\.venv\Scripts\python.exe bot.py
} else {
    python bot.py
}
