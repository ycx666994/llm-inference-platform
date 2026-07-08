$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path .\benchmark\results | Out-Null

$vus = if ($env:VUS) { $env:VUS } else { "1" }
$duration = if ($env:DURATION) { $env:DURATION } else { "20s" }
$name = if ($env:BENCHMARK_NAME) { $env:BENCHMARK_NAME } else { "k6-k8s-mock" }
$model = if ($env:MODEL) { $env:MODEL } else { "facebook/opt-125m" }

$pf = Start-Job -ScriptBlock {
  kubectl -n llm-platform port-forward svc/gateway 18081:8080 --address 127.0.0.1
}

try {
  Start-Sleep -Seconds 6
  docker run --rm `
    -e BASE_URL=http://host.docker.internal:18081 `
    -e API_KEY=sk-demo `
    -e MODEL=$model `
    -e VUS=$vus `
    -e DURATION=$duration `
    -v ${PWD}\benchmark:/scripts `
    grafana/k6:latest run `
    --summary-export /scripts/results/$name-summary.json `
    /scripts/k6-chat.js 2>&1 | Tee-Object -FilePath .\benchmark\results\$name.log
} finally {
  Stop-Job $pf -ErrorAction SilentlyContinue
  Remove-Job $pf -ErrorAction SilentlyContinue
}
