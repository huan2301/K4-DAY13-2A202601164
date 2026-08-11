from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"

TIME_RANGE_MINUTES = 60
REFRESH_SECONDS = 30

LATENCY_THRESHOLD_MS = 3000
TRAFFIC_THRESHOLD_PER_MINUTE = 1
ERROR_RATE_THRESHOLD_PCT = 2
COST_THRESHOLD_USD = 2.5
TOKEN_THRESHOLD = 50_000
QUALITY_THRESHOLD = 0.75


st.set_page_config(
    page_title="Day 13 AI Observability",
    page_icon="📊",
    layout="wide",
)

st.title("Day 13 AI Observability")
st.caption(
    "Nguồn dữ liệu: data/logs.jsonl · "
    "Time range: 60 phút · Auto refresh: 30 giây"
)


def load_logs() -> pd.DataFrame:
    """Đọc JSONL và bỏ qua những dòng log không hợp lệ."""

    if not LOG_PATH.exists():
        return pd.DataFrame()

    records: list[dict] = []

    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        if isinstance(record, dict):
            records.append(record)

    if not records:
        return pd.DataFrame()

    frame = pd.DataFrame(records)

    if "ts" not in frame.columns:
        return pd.DataFrame()

    frame["ts"] = pd.to_datetime(frame["ts"], utc=True, errors="coerce")
    frame = frame.dropna(subset=["ts"])

    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(
        minutes=TIME_RANGE_MINUTES
    )

    return frame[frame["ts"] >= cutoff].copy()


def event_rows(frame: pd.DataFrame, event: str) -> pd.DataFrame:
    """Lọc log theo event mà không gây lỗi khi thiếu cột."""

    if frame.empty or "event" not in frame.columns:
        return pd.DataFrame()

    return frame[frame["event"] == event].copy()


def numeric_column(frame: pd.DataFrame, column: str) -> pd.Series:
    """Chuyển một cột log sang số và loại bỏ giá trị không hợp lệ."""

    if frame.empty or column not in frame.columns:
        return pd.Series(dtype=float)

    return pd.to_numeric(frame[column], errors="coerce").dropna()


def status_text(
    value: float,
    threshold: float,
    operator: str,
    unit: str,
) -> str:
    """Sinh trạng thái SLO để người xem biết metric đang đạt hay vi phạm."""

    if operator == "lte":
        passed = value <= threshold
        symbol = "≤"
    else:
        passed = value >= threshold
        symbol = "≥"

    state = "ĐẠT SLO" if passed else "VI PHẠM SLO"

    return (
        f"{state} · Giá trị {value:.2f} {unit} · "
        f"Ngưỡng {symbol} {threshold:g} {unit}"
    )


def line_chart(
    frame: pd.DataFrame,
    *,
    y: str,
    y_title: str,
    color: str,
    threshold: float | None = None,
) -> alt.Chart:
    """Tạo biểu đồ thời gian và có thể thêm đường threshold."""

    base = (
        alt.Chart(frame)
        .mark_line(point=True, color=color)
        .encode(
            x=alt.X("ts:T", title="Thời gian"),
            y=alt.Y(f"{y}:Q", title=y_title),
            tooltip=[
                alt.Tooltip("ts:T", title="Thời gian"),
                alt.Tooltip(f"{y}:Q", title=y_title, format=".4f"),
            ],
        )
    )

    if threshold is None:
        return base

    threshold_frame = pd.DataFrame({"threshold": [threshold]})

    threshold_line = (
        alt.Chart(threshold_frame)
        .mark_rule(color="#ef4444", strokeDash=[6, 4])
        .encode(y="threshold:Q")
    )

    return base + threshold_line


@st.fragment(run_every=f"{REFRESH_SECONDS}s")
def render_dashboard() -> None:
    frame = load_logs()

    if frame.empty:
        st.warning(
            "Chưa có log trong 60 phút gần nhất. "
            "Hãy chạy API và scripts/load_test.py."
        )
        return

    st.success(
        f"Đã đọc {len(frame)} log records · "
        f"Cập nhật gần nhất: {frame['ts'].max()}"
    )

    responses = event_rows(frame, "response_sent")
    requests = event_rows(frame, "request_received")
    failures = event_rows(frame, "request_failed")

    left, right = st.columns(2)

    # PANEL 1: LATENCY
    with left:
        st.subheader("1. Latency percentiles")

        latencies = numeric_column(responses, "latency_ms")

        if latencies.empty:
            st.info("Chưa có response_sent.latency_ms.")
        else:
            p50 = float(latencies.quantile(0.50))
            p95 = float(latencies.quantile(0.95))
            p99 = float(latencies.quantile(0.99))

            p50_col, p95_col, p99_col = st.columns(3)
            p50_col.metric("P50", f"{p50:.0f} ms")
            p95_col.metric("P95", f"{p95:.0f} ms")
            p99_col.metric("P99", f"{p99:.0f} ms")

            st.caption(
                status_text(
                    p95,
                    LATENCY_THRESHOLD_MS,
                    "lte",
                    "ms",
                )
            )

            latency_chart_data = responses[["ts", "latency_ms"]].copy()
            latency_chart_data["latency_ms"] = pd.to_numeric(
                latency_chart_data["latency_ms"],
                errors="coerce",
            )
            latency_chart_data = latency_chart_data.dropna()

            chart = line_chart(
                latency_chart_data,
                y="latency_ms",
                y_title="Latency (ms)",
                color="#2563eb",
                threshold=LATENCY_THRESHOLD_MS,
            )
            st.altair_chart(chart, use_container_width=True)

    # PANEL 2: TRAFFIC
    with right:
        st.subheader("2. Request traffic")

        total_requests = len(requests)

        if requests.empty:
            request_rate = 0.0
            traffic_by_minute = pd.DataFrame(
                columns=["ts", "requests"]
            )
        else:
            traffic_by_minute = (
                requests.assign(ts=requests["ts"].dt.floor("min"))
                .groupby("ts")
                .size()
                .reset_index(name="requests")
            )
            request_rate = float(traffic_by_minute["requests"].mean())

        st.metric("Request count", total_requests)
        st.metric("Average request rate", f"{request_rate:.2f} req/min")

        st.caption(
            status_text(
                request_rate,
                TRAFFIC_THRESHOLD_PER_MINUTE,
                "gte",
                "req/min",
            )
        )

        if not traffic_by_minute.empty:
            traffic_chart = (
                alt.Chart(traffic_by_minute)
                .mark_bar(color="#0891b2")
                .encode(
                    x=alt.X("ts:T", title="Thời gian"),
                    y=alt.Y("requests:Q", title="Requests/phút"),
                    tooltip=["ts:T", "requests:Q"],
                )
            )
            st.altair_chart(
                traffic_chart,
                use_container_width=True,
            )

    second_left, second_right = st.columns(2)

    # PANEL 3: ERRORS
    with second_left:
        st.subheader("3. Error rate and breakdown")

        request_count = len(requests)
        failure_count = len(failures)

        error_rate = (
            failure_count / request_count * 100
            if request_count
            else 0.0
        )

        error_count_col, error_rate_col = st.columns(2)
        error_count_col.metric("Failed requests", failure_count)
        error_rate_col.metric("Error rate", f"{error_rate:.2f}%")

        st.caption(
            status_text(
                error_rate,
                ERROR_RATE_THRESHOLD_PCT,
                "lte",
                "%",
            )
        )

        if not failures.empty:
            if "error_type" not in failures.columns:
                failures["error_type"] = "Unknown"
            else:
                failures["error_type"] = (
                    failures["error_type"].fillna("Unknown")
                )

            breakdown = (
                failures.groupby("error_type")
                .size()
                .reset_index(name="count")
            )

            error_chart = (
                alt.Chart(breakdown)
                .mark_bar(color="#dc2626")
                .encode(
                    x=alt.X("error_type:N", title="Loại lỗi"),
                    y=alt.Y("count:Q", title="Số lỗi"),
                    tooltip=["error_type:N", "count:Q"],
                )
            )
            st.altair_chart(
                error_chart,
                use_container_width=True,
            )
        else:
            st.info("Không có request_failed trong time range.")

    # PANEL 4: COST
    with second_right:
        st.subheader("4. Cost over time")

        costs = numeric_column(responses, "cost_usd")
        total_cost = float(costs.sum()) if not costs.empty else 0.0

        st.metric("Total cost", f"${total_cost:.6f}")
        st.caption(
            status_text(
                total_cost,
                COST_THRESHOLD_USD,
                "lte",
                "USD",
            )
        )

        if not responses.empty and "cost_usd" in responses.columns:
            cost_data = responses[["ts", "cost_usd"]].copy()
            cost_data["cost_usd"] = pd.to_numeric(
                cost_data["cost_usd"],
                errors="coerce",
            )
            cost_data = cost_data.dropna()
            cost_data["ts"] = cost_data["ts"].dt.floor("min")
            cost_data = (
                cost_data.groupby("ts", as_index=False)["cost_usd"].sum()
            )

            cost_chart = line_chart(
                cost_data,
                y="cost_usd",
                y_title="Cost/phút (USD)",
                color="#7c3aed",
            )
            st.altair_chart(
                cost_chart,
                use_container_width=True,
            )

    third_left, third_right = st.columns(2)

    # PANEL 5: TOKENS
    with third_left:
        st.subheader("5. Input and output tokens")

        tokens_in = numeric_column(responses, "tokens_in")
        tokens_out = numeric_column(responses, "tokens_out")

        tokens_in_total = int(tokens_in.sum()) if not tokens_in.empty else 0
        tokens_out_total = (
            int(tokens_out.sum()) if not tokens_out.empty else 0
        )
        token_total = tokens_in_total + tokens_out_total

        input_col, output_col = st.columns(2)
        input_col.metric("Input tokens", f"{tokens_in_total:,}")
        output_col.metric("Output tokens", f"{tokens_out_total:,}")

        st.caption(
            status_text(
                token_total,
                TOKEN_THRESHOLD,
                "lte",
                "tokens",
            )
        )

        token_data = pd.DataFrame(
            {
                "type": ["Input", "Output"],
                "tokens": [tokens_in_total, tokens_out_total],
            }
        )

        token_chart = (
            alt.Chart(token_data)
            .mark_bar(color="#ea580c")
            .encode(
                x=alt.X("type:N", title="Token type"),
                y=alt.Y("tokens:Q", title="Tokens"),
                tooltip=["type:N", "tokens:Q"],
            )
        )
        st.altair_chart(token_chart, use_container_width=True)

    # PANEL 6: QUALITY
    with third_right:
        st.subheader("6. Quality proxy")

        qualities = numeric_column(responses, "quality_score")
        quality_avg = (
            float(qualities.mean()) if not qualities.empty else 0.0
        )

        st.metric("Average quality score", f"{quality_avg:.2f}")
        st.caption(
            status_text(
                quality_avg,
                QUALITY_THRESHOLD,
                "gte",
                "score",
            )
        )

        if not responses.empty and "quality_score" in responses.columns:
            quality_data = responses[["ts", "quality_score"]].copy()
            quality_data["quality_score"] = pd.to_numeric(
                quality_data["quality_score"],
                errors="coerce",
            )
            quality_data = quality_data.dropna()

            quality_chart = line_chart(
                quality_data,
                y="quality_score",
                y_title="Quality score (0–1)",
                color="#16a34a",
                threshold=QUALITY_THRESHOLD,
            )
            st.altair_chart(
                quality_chart,
                use_container_width=True,
            )


render_dashboard()