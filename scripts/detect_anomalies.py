from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path


PII_DETECTORS = {
    "email": re.compile(r"[\w.-]+@[\w.-]+\.\w+"),
    "phone_vn": re.compile(r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)"),
    "credit_card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
}


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    index = min(len(values) - 1, max(0, round((p / 100) * len(values) + 0.5) - 1))
    return values[index]


def analyze(path: Path, latency_threshold: float, error_threshold: float) -> dict:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    responses = [r for r in records if r.get("event") == "response_sent"]
    requests = [r for r in records if r.get("event") == "request_received"]
    failures = [r for r in records if r.get("event") == "request_failed"]
    latencies = [float(r["latency_ms"]) for r in responses if "latency_ms" in r]
    raw = json.dumps(records, ensure_ascii=False)
    pii_types = sorted(name for name, detector in PII_DETECTORS.items() if detector.search(raw))
    error_rate = (len(failures) / len(requests) * 100) if requests else 0.0
    return {
        "records": len(records),
        "responses": len(responses),
        "p95_latency_ms": percentile(latencies, 95),
        "error_rate_pct": round(error_rate, 2),
        "pii_leaks": pii_types,
        "anomalies": {
            "high_tail_latency": bool(latencies and percentile(latencies, 95) > latency_threshold),
            "high_error_rate": error_rate > error_threshold,
            "pii_detected": bool(pii_types),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect latency, error-rate and PII anomalies in JSONL logs")
    parser.add_argument("--log", type=Path, default=Path("data/logs.jsonl"))
    parser.add_argument("--latency-threshold-ms", type=float, default=3000)
    parser.add_argument("--error-threshold-pct", type=float, default=2)
    args = parser.parse_args()
    if not args.log.exists():
        print(f"Log not found: {args.log}", file=sys.stderr)
        return 2
    result = analyze(args.log, args.latency_threshold_ms, args.error_threshold_pct)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if any(result["anomalies"].values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
