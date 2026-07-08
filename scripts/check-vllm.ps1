$ErrorActionPreference = "Stop"

Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/v1/models" | ConvertTo-Json -Depth 10
