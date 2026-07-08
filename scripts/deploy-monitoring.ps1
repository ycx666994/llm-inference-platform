$ErrorActionPreference = "Stop"

kubectl apply -f .\monitoring\prometheus.yaml
kubectl apply -f .\monitoring\grafana.yaml
kubectl -n llm-platform rollout status deployment/prometheus --timeout=180s
kubectl -n llm-platform rollout status deployment/grafana --timeout=180s
