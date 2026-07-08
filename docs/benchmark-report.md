# Benchmark Report

## Environment

- Date: 2026-07-07 and 2026-07-08
- Cluster: local kind cluster (`kind-llm-platform`)
- Workload: Kubernetes Gateway -> mock vLLM OpenAI-compatible backend; Kubernetes Gateway -> host Docker real vLLM
- Gateway replicas: 1
- mock-vLLM replicas: 1 for mock tests, 0 for hybrid real-vLLM tests
- real vLLM: host Docker container serving `facebook/opt-125m`
- Rate limit: 60 requests/minute per API key
- Benchmark tool: `grafana/k6:latest` Docker image

## Commands

Baseline run:

```powershell
cd C:\Users\HP\llm-inference-platform
$env:VUS="1"
$env:DURATION="20s"
$env:BENCHMARK_NAME="k6-k8s-mock-baseline"
.\scripts\run-k8s-benchmark.ps1
```

Rate-limit run:

```powershell
$env:VUS="5"
$env:DURATION="30s"
$env:BENCHMARK_NAME="k6-k8s-mock"
.\scripts\run-k8s-benchmark.ps1
```

Hybrid real-vLLM baseline:

```powershell
.\scripts\configure-hybrid-real-vllm.ps1
$env:VUS="1"
$env:DURATION="20s"
$env:BENCHMARK_NAME="k6-k8s-hybrid-real-vllm-baseline"
$env:MODEL="facebook/opt-125m"
.\scripts\run-k8s-benchmark.ps1
```

## Results

| Scenario | VUs | Duration | Requests | Success Rate | Failed Rate | Avg Latency | P95 Latency | RPS | Notes |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Baseline | 1 | 20s | 20 | 100.00% | 0.00% | 42.07 ms | 74.72 ms | 0.96 | Below rate limit |
| Rate-limit validation | 5 | 30s | 145 | 41.37% | 58.62% | 47.43 ms | 108.43 ms | 4.79 | Exceeded 60/min API key limit; failures are expected |
| Hybrid real-vLLM baseline | 1 | 20s | 17 | 100.00% | 0.00% | 184.27 ms | 273.81 ms | 0.88 | K8s Gateway -> host Docker vLLM, model `facebook/opt-125m` |

## Observations

- The baseline run passed all HTTP checks and stayed comfortably below the configured rate limit.
- The 5 VU run intentionally exceeded the per-key `60/min` limit. The failed responses validate that Gateway rate limiting is active.
- Prometheus captured Gateway request metrics during the benchmark, including `gateway_requests_total` and `gateway_upstream_requests_total`.
- The hybrid real-vLLM baseline passed all HTTP checks and validated the real vLLM path while the local kind node lacks `nvidia.com/gpu`.
- The real-vLLM average and P95 latency are higher than mock, as expected, because the upstream performs real token generation.

## Artifacts

- `benchmark/results/k6-k8s-mock-baseline.log`
- `benchmark/results/k6-k8s-mock-baseline-summary.json`
- `benchmark/results/k6-k8s-mock.log`
- `benchmark/results/k6-k8s-mock-summary.json`
- `benchmark/results/k6-k8s-hybrid-real-vllm-baseline.log`
- `benchmark/results/k6-k8s-hybrid-real-vllm-baseline-summary.json`

## Next Changes

- Add a dedicated k6 scenario for expected `429` responses so rate-limit tests do not count as failed benchmark checks.
- Add Grafana panels for HTTP 429 rate and per-status-code throughput.
- Run a higher VU real-vLLM test after tuning the per-key rate limit or adding multiple API keys.
- Move real vLLM in-cluster after using a Kubernetes node that exposes `nvidia.com/gpu`.
