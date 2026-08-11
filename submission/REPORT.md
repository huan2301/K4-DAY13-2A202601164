# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

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
| | | | |
