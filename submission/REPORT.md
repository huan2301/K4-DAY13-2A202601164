# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nemo
- Repository URL:https://github.com/huan2301/K4-DAY13-2A202601164
- Commit SHA cuối: `5939226b035bf98e8840d433b0cdcff47393c772`
- Thành viên và vai trò:

| Thành viên       | Mã HV       | Vai trò                         |
| ---------------- | ----------- | ------------------------------- |
| Quách Thanh Hưng | 2A202601532 | Logging & PII                   |
| Lê Đình Việt     | 2A202601528 | Tracing & Prompt Version        |
| Vương Đức Thoại  | 2A202601770 | Dashboard, SLO & Alert          |
| Nguyễn Ngọc Huân | 2A202601164 | QA/CP3, Incident, Report & Demo |

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 sau QA; baseline CP0 trước đó = 30/100
- Tổng số traces: Tối thiểu 10 theo evidence `traces-list.png`; challenge trace ID cần bổ sung từ Langfuse UI
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: Evidence runtime `submission/evidence/dashboard-rag-slow.png`, `dashboard/app.py`

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/correlation-id-evidence.png`
- Evidence PII redaction: `submission/evidence/pii-redaction-evidence.png`
- Evidence trace waterfall: `submission/evidence/trace-baseline.png`, `submission/evidence/trace-candidate.png`
- Giải thích một span đáng chú ý: generation span `run` liên kết trực tiếp với managed prompt `day13-chat`, đồng thời ghi `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source`, token usage và cost. Hai request dùng cùng input nhưng trace metadata lần lượt chứng minh Version 1 (`baseline`) và Version 2 (`candidate`).

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: Version 1 — `baseline`; sau rollback có thêm `production`
- Version/label candidate: Version 2 — `candidate`; đã được chuyển sang `production` trước khi rollback
- Trace ID của mỗi version:
  - Baseline / Version 1: `2c764e4f99f6eb27abc453ad4d619d91`
  - Candidate / Version 2: `2b3876aa62212f646232790c81f7c429`
- Bằng chứng đổi label hoặc rollback:
  - `submission/evidence/production-v2.png`: label `production` được chuyển sang Version 2.
  - `submission/evidence/rollback-production-v1.png`: rollback `production` về Version 1.
  - `submission/evidence/traces-list.png`: danh sách dữ liệu tracing sau load test.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ 6/6 panel.
- Evidence validator: `submission/evidence/dashboard-validator.png`
- Evidence baseline: `submission/evidence/dashboard-baseline.png`
- Evidence incident: `submission/evidence/dashboard-rag-slow.png`

### SLO đã chọn

Nhóm sử dụng cửa sổ SLO 28 ngày với các mục tiêu:

- P95 latency không vượt quá 3000 ms.
- Error rate không vượt quá 2%.
- Daily cost không vượt quá 2.5 USD.
- Quality score trung bình ít nhất 0.75.

P95 được sử dụng thay cho average latency vì average có thể che khuất
một nhóm nhỏ request rất chậm. Error rate đo tỷ lệ request thất bại trên
tổng request nhận được. Quality score được theo dõi vì AI API có thể trả
HTTP 200 nhưng nội dung vẫn không đáp ứng yêu cầu người dùng.

### Alert rules và runbook

Nhóm triển khai ba alert:

1. HighTailLatency: P95 > 3000 ms trong 5 phút.
2. HighRequestErrorRate: error rate > 2% trong 5 phút.
3. LowResponseQuality: quality score trung bình < 0.75 trong 10 phút.

Mỗi alert có severity, owner, user impact, mitigation và runbook điều tra
theo luồng Metrics → Traces → Logs.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1` (cohort K4)
- Incident: `rag_slow`, affected feature `monitoring`
- Triệu chứng từ metrics: `latency_p95=2651ms`, `latency_p99=2651ms`, vượt threshold challenge `2000ms`; error rate `0%`; quality average `0.8667`. Chi tiết: `submission/evidence/cp3-metrics.txt`
- Trace ID liên quan: cần mở Langfuse và ghi trace ID của một session `k4-challenge-s01` đến `k4-challenge-s05`; hiện chưa có trong log export local
- Log line/correlation ID liên quan: `req-0fe877de`, `req-abc39265`, `req-dfeaab0a`, `req-3fe3ecc8`, `req-02f99ff2`; chi tiết: `submission/evidence/cp3-log.txt`
- Root cause: incident `rag_slow` thêm khoảng 2,5 giây vào retrieval/RAG, làm tăng tail latency nhưng không gây request failure
- Fix action: chạy `python scripts/inject_incident.py --disable`, API xác nhận `rag_slow=false`
- Preventive measure: alert P95, đo riêng retrieval span, timeout retrieval và fallback khi retrieval chậm

## 6.1 QA/CP3 evidence

- Kết quả test: `submission/evidence/qa-results.txt`
- Phân tích root cause: `submission/evidence/cp3-root-cause.md`
- Kết quả metrics: `submission/evidence/cp3-metrics.txt`
- Correlation log: `submission/evidence/cp3-log.txt`

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên       | Phần việc                                                                                                                                                                                                                                                              | Commit/PR                                                                                                                    | Điều đã học                                                                                                                                                                                                                                                            |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Lê Đình Việt     | Tích hợp trace metadata, kiểm chứng managed prompt Version 1/2, chuyển label production, rollback và thu thập evidence                                                                                                                                                 | `ffd8916`, `54c8c70`                                                                                                         | Phân biệt trace/span, liên kết prompt version với generation, dùng label để triển khai và rollback prompt mà không sửa code ứng dụng                                                                                                                                   |
| Nguyễn Ngọc Huân | Chạy QA toàn hệ thống, chạy challenge chính thức `rag_slow`, đối chiếu metrics → traces → logs, xác định root cause, kiểm tra recovery và hoàn thiện evidence/report                                                                                                   | `https://github.com/huan2301/K4-DAY13-2A202601164/commit/323a9e12934f0b5e44ef0b11d380162af8b2dd46`, Working tree QA evidence | Xác định slow retrieval qua P95/P99 và correlation ID; phân biệt lỗi latency với lỗi request                                                                                                                                                                           |
| Quách Thanh Hưng | Cài đặt Correlation ID Middleware, enrich log context, cấu hình regex patterns che PII và nâng cấp che PII toàn cục                                                                                                                                                    | `7382b69`                                                                                                                    | Phải xử lý middleware để tránh data leakage, che PII phải che toàn bộ các dữ liệu mà có khả năng định danh cá nhân                                                                                                                                                     |
| Vương Đức Thoại  | Xây dựng dashboard runtime đọc `data/logs.jsonl` với 6 panel latency, traffic, error, cost, token và quality; cấu hình SLO 28 ngày; xây dựng ba alert theo triệu chứng và runbook; kiểm tra dashboard contract, chạy baseline/incident `rag_slow` và thu thập evidence | `d7149e6`, `70c2e88`                                                                                                         | Hiểu cách dùng P50/P95/P99 để quan sát tail latency; chuyển SLI thành SLO và threshold có thể đo; thiết kế alert có condition, duration, severity, owner và mitigation; điều tra sự cố theo luồng Metrics → Traces → Logs và so sánh dashboard baseline với `rag_slow` |

## 8. Bonus - Cost Optimization, Audit Log and Custom Automation

- Cost optimization: added an output-token cap controlled by `COST_OPTIMIZATION_ENABLED` and `MAX_OUTPUT_TOKENS`.
- Before with `cost_spike`: total cost `$0.0329`, output tokens `2164`.
- After with optimization enabled: total cost `$0.0139`, output tokens `900`.
- Cost reduction: approximately `57.8%`; quality proxy remained `0.8`.
- Evidence: `submission/evidence/bonus-cost-before-after.md`.

- Audit log: added `app/audit.py`; incident enable/disable events are written to `data/audit.jsonl` without PII.
- Evidence: `submission/evidence/bonus-audit-log-sample.jsonl`.

- Custom automation: added `scripts/detect_anomalies.py` to detect P95 latency, error-rate and PII anomalies from `data/logs.jsonl`.
- Result: P95 `2650ms`, error rate `0%`, PII leaks `0`.
- Evidence: `submission/evidence/bonus-anomaly-output.json`.
