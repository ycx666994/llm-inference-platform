$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\.."

kubectl get deployment/mock-vllm -n llm-platform *> $null
if ($LASTEXITCODE -eq 0) {
  kubectl scale deployment/mock-vllm -n llm-platform --replicas=0
}

kubectl get deployment/vllm -n llm-platform *> $null
if ($LASTEXITCODE -eq 0) {
  kubectl scale deployment/vllm -n llm-platform --replicas=0
}

$env:VLLM_BASE_URL = if ($env:VLLM_BASE_URL) { $env:VLLM_BASE_URL } else { "http://host.docker.internal:8000" }
$env:MODEL = if ($env:MODEL) { $env:MODEL } else { "facebook/opt-125m" }
.\scripts\configure-hybrid-real-vllm.ps1

kubectl get deploy,pods,svc,endpoints -n llm-platform
