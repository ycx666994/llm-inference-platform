$ErrorActionPreference = "Stop"

kubectl apply -k .\k8s\real-vllm
kubectl -n llm-platform rollout status deployment/vllm --timeout=600s
kubectl -n llm-platform rollout status deployment/gateway --timeout=180s
