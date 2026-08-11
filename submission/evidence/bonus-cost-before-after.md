# Bonus: cost optimization before/after

The optimization caps generated output tokens with `MAX_OUTPUT_TOKENS` when
`COST_OPTIMIZATION_ENABLED=true`. The default cap is 180 tokens. The
`cost_spike` incident was used for both measurements, with five identical
requests per run and a fresh API process each time.

## Before

Configuration: `COST_OPTIMIZATION_ENABLED=false`

```json
{"traffic":5,"latency_p50":2157.0,"latency_p95":2164.0,"avg_cost_usd":0.0066,"total_cost_usd":0.0329,"tokens_in_total":145,"tokens_out_total":2164,"error_rate_pct":0.0,"quality_avg":0.8}
```

## After

Configuration: `COST_OPTIMIZATION_ENABLED=true`, `MAX_OUTPUT_TOKENS=180`

```json
{"traffic":5,"latency_p50":2155.0,"latency_p95":2165.0,"avg_cost_usd":0.0028,"total_cost_usd":0.0139,"tokens_in_total":145,"tokens_out_total":900,"error_rate_pct":0.0,"quality_avg":0.8}
```

## Result

- Total cost reduced from `$0.0329` to `$0.0139`.
- Reduction: `$0.0190` or approximately `57.8%`.
- Output tokens reduced from `2164` to `900`.
- Quality proxy remained `0.8` in both runs.
- The optimization is controlled by environment variables and does not alter
  the official challenge configuration.
