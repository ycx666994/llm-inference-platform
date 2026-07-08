$ErrorActionPreference = "Stop"

Start-Process -WindowStyle Minimized -FilePath powershell -ArgumentList "-NoExit", "-Command", "kubectl -n llm-platform port-forward svc/prometheus 9090:9090"
Start-Process -WindowStyle Minimized -FilePath powershell -ArgumentList "-NoExit", "-Command", "kubectl -n llm-platform port-forward svc/grafana 3000:3000"

Write-Host "Prometheus: http://127.0.0.1:9090"
Write-Host "Grafana:    http://127.0.0.1:3000"
Write-Host "Grafana login: admin / admin"
Write-Host "Close the two minimized PowerShell windows to stop port-forwarding."
