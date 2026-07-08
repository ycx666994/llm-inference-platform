$ErrorActionPreference = "Stop"

$namespace = if ($env:NAMESPACE) { $env:NAMESPACE } else { "llm-platform" }
$vllmBaseUrl = if ($env:VLLM_BASE_URL) { $env:VLLM_BASE_URL } else { "http://host.docker.internal:8000" }
$model = if ($env:MODEL) { $env:MODEL } else { "facebook/opt-125m" }

kubectl create configmap gateway-config `
  -n $namespace `
  --from-literal=VLLM_BASE_URL=$vllmBaseUrl `
  --from-literal=DEFAULT_MODEL=$model `
  --from-literal=RATE_LIMIT_PER_MINUTE=60 `
  --from-literal=UPSTREAM_TIMEOUT_SECONDS=120 `
  --dry-run=client `
  -o yaml | kubectl apply -f -

kubectl get deployment/mock-vllm -n $namespace *> $null
if ($LASTEXITCODE -eq 0) {
  kubectl scale deployment/mock-vllm -n $namespace --replicas=0
}

kubectl get deployment/vllm -n $namespace *> $null
if ($LASTEXITCODE -eq 0) {
  kubectl scale deployment/vllm -n $namespace --replicas=0
}

kubectl rollout restart deployment/gateway -n $namespace
kubectl rollout status deployment/gateway -n $namespace --timeout=90s

Write-Host "Gateway now forwards to $vllmBaseUrl with default model $model"
