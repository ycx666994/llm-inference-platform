Set-Location "$PSScriptRoot\..\gateway"

$env:API_KEYS = "sk-demo"
$env:VLLM_BASE_URL = "http://127.0.0.1:8000"
$env:DEFAULT_MODEL = "facebook/opt-125m"
$env:RATE_LIMIT_PER_MINUTE = "60"

.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080
