# Real vLLM Runbook

## Target

Replace the mock OpenAI-compatible backend with real vLLM serving a real model.

Initial model:

```text
facebook/opt-125m
```

This model is intentionally small so the platform can validate real model serving before moving to larger Qwen/Llama models.

`facebook/opt-125m` does not ship a chat template, so this project provides a minimal template at:

```text
configs/opt-chat-template.jinja
```

## Docker Path

```powershell
cd C:\Users\HP\llm-inference-platform
.\scripts\start-real-vllm-docker.ps1
```

Then run the Gateway with:

```powershell
cd C:\Users\HP\llm-inference-platform\gateway
$env:API_KEYS="sk-demo"
$env:VLLM_BASE_URL="http://127.0.0.1:8000"
$env:DEFAULT_MODEL="facebook/opt-125m"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Validated locally on 2026-07-08:

- Docker Desktop served `facebook/opt-125m` with GPU runtime.
- `GET http://127.0.0.1:8000/v1/models` returned the model.
- `POST http://127.0.0.1:8080/v1/chat/completions` through the Gateway returned HTTP 200.
- Gateway metrics recorded `gateway_upstream_requests_total{model="facebook/opt-125m",status_code="200"}`.

## Kubernetes Path

The real-vLLM overlay is ready here:

```text
k8s/real-vllm
```

Deploy:

```powershell
cd C:\Users\HP\llm-inference-platform
.\scripts\deploy-real-vllm-k8s.ps1
```

## Hybrid Kubernetes Path

Use this on local kind when the node does not expose `nvidia.com/gpu`, but Docker Desktop can run vLLM with GPU on the host.

Keep host Docker vLLM running:

```powershell
cd C:\Users\HP\llm-inference-platform
.\scripts\start-real-vllm-docker.ps1
```

Point the in-cluster Gateway at the host vLLM endpoint:

```powershell
.\scripts\configure-hybrid-real-vllm.ps1
```

Expose the K8s Gateway locally:

```powershell
kubectl -n llm-platform port-forward svc/gateway 8081:8080
```

Test:

```powershell
$body = @{ model="facebook/opt-125m"; messages=@(@{role="user"; content="Say hello in one short sentence."}); max_tokens=32 } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8081/v1/chat/completions" -Headers @{Authorization="Bearer sk-demo"} -ContentType "application/json" -Body $body
```

## Current Environment Notes

On this machine, `vllm/vllm-openai:latest` is large, but the image is now present locally and the Docker GPU path has been validated.

Local kind status:

- `k8s/real-vllm` was applied successfully.
- The in-cluster `vllm` Pod could not schedule because the kind node does not expose `nvidia.com/gpu`.
- The local demo therefore uses hybrid mode: Kubernetes Gateway -> host Docker vLLM.
- The in-cluster `vllm` Deployment should stay scaled to `0` until a GPU-enabled Kubernetes node is available.
