# Checklist Tracing & Prompt Version

Tài liệu này là quy trình thực hành cho vai trò **Tracing & Prompt Version**.

## 1. Cấu hình Langfuse

Mở `.env` và điền key của project được Lab Coach cung cấp:

```dotenv
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PROMPT_NAME=day13-chat
LANGFUSE_PROMPT_LABEL=production
```

Không commit `.env` hoặc chụp ảnh làm lộ key. Kiểm tra kết nối bằng cách chạy API rồi mở `http://127.0.0.1:8000/health`. Giá trị `tracing_enabled` phải là `true`.

## 2. Tạo hai phiên bản prompt

Trong Langfuse, vào **Prompt Management** và tạo text prompt tên `day13-chat`.

Version 1:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

Gắn hai label `baseline` và `production` cho version 1.

Tạo version 2 với thay đổi nhỏ về định dạng, nhưng giữ nguyên ba biến:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}

Answer clearly and concisely in no more than three sentences.
```

Gắn label `candidate` cho version 2.

## 3. Sinh trace cho baseline

Đặt trong `.env`:

```dotenv
LANGFUSE_PROMPT_LABEL=baseline
```

Khởi động lại API để nạp cấu hình mới:

```powershell
uvicorn app.main:app --reload --env-file .env
```

Ở terminal thứ hai, gửi một input cố định:

```powershell
$body = @{
    user_id = "trace-role-user"
    session_id = "prompt-comparison"
    feature = "monitoring"
    message = "How do metrics, traces, and logs help investigate an incident?"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
    -Uri http://127.0.0.1:8000/chat `
    -ContentType "application/json" `
    -Body $body
```

Mở trace mới trên Langfuse và lưu trace ID. Metadata phải có:

- `prompt_name=day13-chat`
- `prompt_label=baseline`
- `prompt_version=1`
- `prompt_source=langfuse`

## 4. Sinh trace cho candidate

Đổi `.env` thành `LANGFUSE_PROMPT_LABEL=candidate`, khởi động lại API và gửi lại **đúng input ở bước 3**. Lưu trace ID thứ hai và kiểm tra metadata trỏ đến version 2.

## 5. Chứng minh đổi label và rollback

1. Trên Langfuse, chuyển label `production` từ version 1 sang version 2.
2. Đặt `.env` về `LANGFUSE_PROMPT_LABEL=production`, khởi động lại API và gửi request.
3. Kiểm tra trace production đang dùng version 2 và chụp ảnh bằng chứng.
4. Chuyển label `production` về version 1.
5. Gửi lại request, kiểm tra trace production đã dùng version 1 và chụp ảnh rollback.

## 6. Thu thập đủ trace và bằng chứng

Chạy load test để tổng số trace đạt ít nhất 10:

```powershell
python scripts/load_test.py
```

Lưu trong `submission/evidence/`:

- Ảnh danh sách prompt version 1 và 2 cùng các label.
- Ảnh trace dùng `baseline`.
- Ảnh trace dùng `candidate`.
- Ảnh trước và sau khi rollback label `production`.

Điền prompt name, version/label, hai trace ID và đường dẫn ảnh vào mục **Prompt versioning** của `submission/REPORT.md`.

## 7. Tự kiểm tra trước khi commit

```powershell
python -m pytest -q tests/test_tracing_adapter.py tests/test_prompt_management.py tests/test_agent_prompt_trace.py
git status --short
git check-ignore .env
```

Lệnh cuối phải in ra `.env`, xác nhận file chứa key không được Git theo dõi.
