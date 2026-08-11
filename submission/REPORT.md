# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nemo
- Repository URL: https://github.com/huan2301/K4-DAY13-2A202601164
- Commit SHA cuối: cập nhật theo `HEAD` của nhánh `main` khi nộp bài
- Thành viên và vai trò: Lê Đình Việt - Tracing & Prompt Version

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces: Đã sinh 10 request thành công bằng `scripts/load_test.py`, ngoài hai request đối chiếu baseline/candidate; Langfuse hiển thị 73 span trong khoảng chụp evidence.
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
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
- Evidence dashboard: `submission/evidence/dashboard-baseline.png`
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

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Lê Đình Việt | Tích hợp trace metadata, kiểm chứng managed prompt Version 1/2, chuyển label production, rollback và thu thập evidence | `ffd8916`, `54c8c70` | Phân biệt trace/span, liên kết prompt version với generation, dùng label để triển khai và rollback prompt mà không sửa code ứng dụng |
