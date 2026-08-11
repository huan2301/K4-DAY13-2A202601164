# CP3 root-cause analysis

## Symptom

The official challenge `day13-k4-observability-v1` enabled `rag_slow` for the
`monitoring` feature. After five official challenge requests, P95 and P99
latency were 2651 ms, above the challenge threshold of 2000 ms. Error rate was
0% and average quality was 0.8667.

Evidence: [cp3-metrics.txt](cp3-metrics.txt)

## Trace and log correlation

The challenge requests were recorded with these correlation IDs:

- `req-0fe877de` / `k4-challenge-s02` / 2651 ms
- `req-abc39265` / `k4-challenge-s05` / 2650 ms
- `req-dfeaab0a` / `k4-challenge-s04` / 2651 ms
- `req-3fe3ecc8` / `k4-challenge-s01` / 2650 ms
- `req-02f99ff2` / `k4-challenge-s03` / 2651 ms

Evidence: [cp3-log.txt](cp3-log.txt). A Langfuse trace ID for one of these
challenge requests still needs to be captured from the hosted tracing UI.

## Root cause

The `rag_slow` incident adds a 2.5-second delay in retrieval. The repeated
approximately 2.65-second response latency and 0% error rate are consistent
with a slow retrieval span rather than an LLM request failure.

## Fix and prevention

- Fix performed: disabled the official incident with
  `python scripts/inject_incident.py --disable`.
- Prevention: alert on P95 latency, instrument retrieval duration separately,
  enforce a retrieval timeout, and provide a fallback when retrieval is slow.
