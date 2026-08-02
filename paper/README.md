# Paper: A Cloud-Native Gateway Architecture for LLM Inference Serving

This directory contains the academic paper accompanying the `llm-inference-platform` project.

## Files

| File | Description |
|------|-------------|
| `llm_gateway_paper.tex` | LaTeX source (IEEEtran format) |
| `llm_gateway_paper.pdf` | Compiled PDF (13 pages, ~10,000 words) |

## Abstract

Deploying LLMs in production requires more than a model serving engine. This paper presents a cloud-native inference gateway that separates platform concerns (authentication, rate limiting, observability) from model serving, supporting mock/real/hybrid deployment modes from a single codebase. Evaluation shows the gateway adds ~3 ms median overhead and enforces per-key rate limits correctly under concurrent load.

## Target Venue

CCF-recommended B-class international journal (JSS / SPE / IST).

## Compilation

```bash
pdflatex llm_gateway_paper.tex
pdflatex llm_gateway_paper.tex
pdflatex llm_gateway_paper.tex
```
