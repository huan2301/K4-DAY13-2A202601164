# Alert và Runbook

Các alert trong tài liệu này dựa trên triệu chứng người dùng và SLO.
Quy trình điều tra chung là Metrics → Traces → Logs → Root cause.

## Alert 1

- Tên: HighTailLatency
- Severity: Warning
- SLI/SLO liên quan: P95 latency ≤ 3000 ms
- Điều kiện: P95 của `response_sent.latency_ms` lớn hơn 3000 ms liên tục 5 phút
- Ảnh hưởng người dùng: Người dùng phải chờ lâu hơn để nhận câu trả lời
- Owner: YOUR_NAME

### Ba bước kiểm tra đầu tiên

1. Mở panel Latency và xác định thời gian P95 bắt đầu vượt 3000 ms.
2. Mở một trace chậm trong cùng khoảng thời gian, so sánh duration của agent, retrieval và LLM.
3. Tìm log có cùng correlation ID để kiểm tra incident, error và metadata liên quan.

### Mitigation tạm thời

- Giảm concurrency nếu hệ thống đang quá tải.
- Tắt incident practice nếu incident đang bật.
- Dùng retrieval fallback hoặc bỏ qua retrieval nếu thành phần này đang quá chậm.
- Rollback thay đổi gần nhất nếu latency tăng ngay sau deployment.

### Xác nhận phục hồi

Alert được xem là phục hồi khi P95 trở lại dưới hoặc bằng 3000 ms trong ít nhất 10 phút.

## Alert 2

- Tên: HighRequestErrorRate
- Severity: Critical
- SLI/SLO liên quan: Error rate ≤ 2%
- Điều kiện: `request_failed / request_received * 100` lớn hơn 2% liên tục 5 phút
- Ảnh hưởng người dùng: Một phần request không nhận được câu trả lời
- Owner: YOUR_NAME

### Ba bước kiểm tra đầu tiên

1. Mở panel Error rate để xác định thời gian bắt đầu và loại lỗi chiếm nhiều nhất.
2. Mở trace lỗi trong cùng khoảng thời gian để xác định component thất bại.
3. Tìm `request_failed` log có cùng correlation ID và kiểm tra `error_type`.

### Mitigation tạm thời

- Tắt incident hoặc feature gây lỗi nếu đã xác định được.
- Chuyển sang fallback khi retrieval hoặc tool ngoài không khả dụng.
- Giảm traffic hoặc concurrency nếu dependency bị quá tải.
- Rollback deployment gần nhất nếu lỗi xuất hiện sau thay đổi.

### Xác nhận phục hồi

Alert được xem là phục hồi khi error rate trở lại dưới hoặc bằng 2% trong ít nhất 10 phút.

## Alert 3

- Tên: LowResponseQuality
- Severity: Warning
- SLI/SLO liên quan: Quality score trung bình ≥ 0.75
- Điều kiện: Trung bình `response_sent.quality_score` nhỏ hơn 0.75 liên tục 10 phút
- Ảnh hưởng người dùng: Câu trả lời có thể không liên quan, quá ngắn hoặc thiếu ngữ cảnh
- Owner: Vương Đức Thoại

### Ba bước kiểm tra đầu tiên

1. Mở panel Quality và xác định feature hoặc khoảng thời gian bị giảm điểm.
2. Mở trace có quality score thấp để kiểm tra prompt version, retrieved documents và model metadata.
3. Tìm log cùng correlation ID để kiểm tra feature, model, token và prompt metadata.

### Mitigation tạm thời

- Rollback label `production` về prompt version ổn định.
- Chuyển sang prompt baseline nếu candidate có quality thấp.
- Kiểm tra retrieval có trả đúng tài liệu hay không.
- Giới hạn rollout của prompt candidate trong khi điều tra.

### Xác nhận phục hồi

Alert được xem là phục hồi khi quality score trung bình lớn hơn hoặc bằng 0.75 trong ít nhất 15 phút.