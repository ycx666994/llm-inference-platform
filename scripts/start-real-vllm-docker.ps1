$ErrorActionPreference = "Stop"

$model = if ($env:MODEL) { $env:MODEL } else { "facebook/opt-125m" }
$containerName = "llm-platform-real-vllm"
$cacheDir = Join-Path $env:USERPROFILE ".cache\huggingface"
$configDir = Join-Path $PSScriptRoot "..\configs"
$chatTemplate = if ($env:CHAT_TEMPLATE) { $env:CHAT_TEMPLATE } else { "/etc/vllm/opt-chat-template.jinja" }

New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null

$existing = docker ps -a --filter "name=^/$containerName$" --format "{{.Names}}"
if ($existing -eq $containerName) {
  docker rm -f $containerName | Out-Null
}

$containerId = docker run `
  -d `
  --name $containerName `
  --gpus all `
  --ipc=host `
  -p 8000:8000 `
  -v "${cacheDir}:/root/.cache/huggingface" `
  -v "${configDir}:/etc/vllm:ro" `
  vllm/vllm-openai:latest `
  $model `
  --host 0.0.0.0 `
  --port 8000 `
  --max-model-len 1024 `
  --gpu-memory-utilization 0.75 `
  --chat-template $chatTemplate

Write-Host "Started $containerName ($containerId)"
Write-Host "Follow logs: docker logs -f $containerName"
