$ErrorActionPreference = "Stop"

$model = if ($env:MODEL) { $env:MODEL } else { "Qwen/Qwen2.5-0.5B-Instruct" }
$containerName = "llm-platform-vllm"
$cacheDir = Join-Path $env:USERPROFILE ".cache\huggingface"

New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null

$existing = docker ps -a --filter "name=^/$containerName$" --format "{{.Names}}"
if ($existing -eq $containerName) {
  docker rm -f $containerName | Out-Null
}

docker run `
  -d `
  --name $containerName `
  --gpus all `
  --ipc=host `
  -p 8000:8000 `
  -v "${cacheDir}:/root/.cache/huggingface" `
  vllm/vllm-openai:latest `
  --model $model `
  --host 0.0.0.0 `
  --port 8000 `
  --max-model-len 2048

Write-Host "Started container: $containerName"
Write-Host "Follow logs with: docker logs -f $containerName"
