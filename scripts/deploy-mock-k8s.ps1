$ErrorActionPreference = "Stop"

kubectl apply -k .\k8s\mock
kubectl -n llm-platform rollout status deployment/mock-vllm --timeout=120s
kubectl -n llm-platform rollout status deployment/gateway --timeout=120s
