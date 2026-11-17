# Báo cáo cá nhân — Nguyễn Thế Cường

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thế Cường
- MSSV: 2A202603355
- Email: 26ai.cuongnt2@vinuni.edu.vn
- GitHub: Chill2004

## 2. Phần việc phụ trách

Phụ trách Shape A — Workflow trong `src/lab8/shapes/workflow.py`, bổ sung test cho Workflow trong `src/tests/test_workflow.py`, kiểm tra trace và chạy crash suite. Theo phân công nhóm, phụ trách thêm việc tích hợp và kiểm tra bài nộp sau khi nhận phần Single của Trí và Orchestrator của Ánh. Phần tích hợp toàn nhóm chưa được xác nhận hoàn tất tại thời điểm lập báo cáo này.

## 3. Đóng góp cụ thể

### 3.1. Triển khai Workflow

Thay stub `not_implemented` bằng quy trình Python cố định, giữ nguyên chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None)`:

1. Đọc claim bằng `get_claim_view`; claim không tồn tại trả `failed`.
2. Thiếu `order_id` trả `needs_info`; không suy đoán mã đơn từ ticket.
3. Tra đơn bằng `lookup_order` theo principal; đơn không tồn tại hoặc ngoài phạm vi quyền trả `escalated`.
4. Tính quote bằng `compute_compensation` từ dữ liệu đơn và policy hiện hành; không lấy số ngày trễ hoặc số tiền trong ticket làm căn cứ.
5. Quote bằng 0 trả `denied`, không gọi host ghi tiền.
6. Quote dương được truyền đầy đủ vào `issue_refund`. Host kiểm approval, trần theo đơn và idempotency. Host từ chối thì trả `denied`; conflict trả `failed`; thành công trả `resolved`.

Workflow không cần gọi model. Code tính quote; host quyết định số tiền thực ghi và ghi ledger. `proposal_amount` giữ quote đầy đủ, kể cả khi approval giới hạn số tiền thực hoàn. Shape không tự trừ khoản đã hoàn trước đó để tránh host trừ lần thứ hai.

Truyền `crash_at` vào `issue_refund` và không bắt `InjectedCrash`. Dùng `finally` để đóng kết nối DB. Mọi nhánh trả kết quả dùng `common.finish()` để lấy effect/audit từ ledger và ghi trace.

Trace ghi các event `claim_lookup`, `order_lookup`, `quote`, `decision`. Không ghi nguyên claim, order hay ticket; chỉ ghi thông tin cần thiết để kiểm tra quyết định, tránh đưa secret và dữ liệu cá nhân vào log.

### 3.2. Bổ sung kiểm thử

Thêm 7 hàm test, tương ứng 8 trường hợp chạy; test đầu tiên chạy với hai seed. Các test dùng DB tạm từ fixture `public_db` và ghi trace vào thư mục tạm, không sửa dữ liệu public trong `src/data/`.

| Hàm test trong `src/tests/test_workflow.py` | Nội dung kiểm tra |
| --- | --- |
| `test_workflow_ignores_ticket_instructions` | Seed 11 và 55: ticket yêu cầu bỏ qua policy, khai trễ 99 ngày và yêu cầu hoàn 999999 VND; đơn thực chỉ trễ 2 ngày nên vẫn denied, quote 0, không refund |
| `test_workflow_does_not_infer_missing_order_from_ticket` | Thiếu `order_id` dù ticket có mã đơn: needs_info, không refund và có trace hợp lệ |
| `test_workflow_ticket_secret_stays_out_of_outputs` | Token canary giả trong ticket không xuất hiện trong RunResult, trace, file cùng tiền tố run id, stdout hoặc stderr; claim hợp lệ vẫn resolved |
| `test_workflow_expired_approval_stays_denied_on_retries` | Retry cùng DB với seed 11, 22, 55: approval hết hạn luôn bị từ chối, quote vẫn 35000, không refund và có audit policy_denied |
| `test_workflow_low_approval_preserves_quote_and_caps_refund_on_retry` | Quote 35000, approval giới hạn thực hoàn 20000; retry với seed khác vẫn một refund và một audit committed |
| `test_workflow_rejects_approval_borrowed_from_another_claim` | Gán approval của claim khác trong DB tạm: denied, không refund, audit có lý do approval_claim_mismatch |
| `test_workflow_crash_resume_then_retries_are_idempotent` | Crash sau effect trước checkpoint, resume rồi retry 3 lần trên cùng DB: giữ nguyên một refund 35000 và một audit committed; checkpoint được khôi phục và trace hợp lệ |

### 3.3. Xử lý lỗi và kiểm chứng

Khi chạy pytest trên Windows, gặp `PermissionError: [WinError 5]` do không truy cập được thư mục `%TEMP%/pytest-of-Admin`. Chuyển thư mục tạm pytest sang nơi có quyền ghi bằng các lệnh PowerShell sau, chạy tại `src/`:

```powershell
$env:PYTEST_DEBUG_TEMPROOT = Join-Path (Get-Location) '.pytest_cache\temp'
New-Item -ItemType Directory -Path $env:PYTEST_DEBUG_TEMPROOT -Force | Out-Null
```

Sau khi chuyển, test chạy được. Biến môi trường chỉ có hiệu lực trong terminal hiện tại. Không sửa `pytest.ini` để loại bỏ bộ test student; `248 deselected` trong lệnh mặc định là hành vi cấu hình của repo.

Trong quá trình bổ sung test crash, phát hiện phép so sánh ban đầu không đúng giữa toàn bộ dòng DB và effect trong RunResult. Sửa test để so sánh bốn field theo contract của effect, đồng thời giữ phép kiểm tra toàn bộ dòng ledger không đổi sau mỗi lần retry. Không sửa host để làm test pass.

## 4. Bằng chứng

Các kết quả dưới đây lấy từ output chạy thực tế đã được xác nhận trong quá trình làm bài; không phải kết quả benchmark.

| Lệnh chạy trong `src/` | Kết quả đã xác nhận |
| --- | --- |
| `python -m pytest -q -m student -o addopts= -k workflow` | 62 passed ở lượt kiểm tra Workflow trước khi bổ sung toàn bộ test riêng |
| `python -m pytest -q tests/test_workflow.py` | 8 passed in 0.55s |
| `python -m pytest -q` | 62 passed, 248 deselected in 3.83s; gồm 54 test mặc định ban đầu và 8 test bổ sung |
| `python -m lab8.crash_test --count 20 --out reports/crash.json` | crash_safety 20/20; đối chiếu `src/reports/crash.json` có count = 20, passed = 20 |
| `python -m lab8.run --shape workflow --claim-id C-001 --seed 11 --db data/cuong_review.sqlite` | Run id `R-workflow-C-001-s11`; trace có 4 event, quote 35000 theo SHIP-LATE-03, quyết định resolved |

Hai bộ test mặc định và student là các phạm vi khác nhau. 8 test riêng đã nằm trong kết quả 62 test mặc định, không cộng hai kết quả này với nhau. Bộ student có 62 trường hợp Workflow riêng; các lần chạy trên không chứng minh toàn bộ ba shape nhóm viết đã hoàn thành.

Crash suite có sẵn chủ yếu kiểm host và một kịch bản swarm. Test crash riêng trong `test_workflow.py` bổ sung bằng chứng cho chuỗi chạy qua chính Workflow, không chỉ gọi host trực tiếp.

Trace C-001 đã được đọc kiểm tra và không thấy secret hay dữ liệu cá nhân trong file này. Kết luận đó không đại diện cho mọi trace hoặc bộ hidden. Trace và SQLite dùng kiểm tra cục bộ không commit; giữ `crash.json` do công cụ sinh làm bằng chứng nộp bài.

## 5. Công cụ AI đã dùng

Sử dụng ChatGPT/Codex để giải thích đề, phân công, gợi ý và hỗ trợ triển khai Workflow, viết test, đọc traceback, rà trace và soạn báo cáo từ bằng chứng thực tế. Code và test có sự hỗ trợ của AI.

Tự kiểm chứng bằng cách chạy pytest trong terminal, gửi output để đối chiếu, chạy crash suite và chạy một claim để kiểm tra trace. Khi test crash do AI hỗ trợ viết thất bại vì so sánh sai cấu trúc dữ liệu, đối chiếu contract với dữ liệu DB rồi sửa test và chạy lại.

AI chỉ là công cụ hỗ trợ phát triển; Workflow không gọi model thật hoặc sử dụng API key. Không dùng AI để tạo số liệu benchmark, hash commit hoặc tự đánh giá cá nhân chưa được xác nhận.

## 6. Tự đánh giá

- Những nội dung bản thân đã hiểu và có thể giải thích lại: Tôi đã nắm được luồng xử lý cơ bản của Workflow từ đọc claim, kiểm tra đơn, tính quote đến gọi host và trả kết quả. Tôi hiểu rằng ticket là dữ liệu người dùng, không phải chỉ dẫn điều khiển hệ thống; số tiền phải được tính từ dữ liệu đơn và policy. Quote được truyền đầy đủ cho host để kiểm approval, trần hoàn tiền và chống ghi trùng.

- Những nội dung còn cần hỗ trợ hoặc luyện tập: Tôi cần luyện thêm cách tự viết test, đọc traceback và phân biệt dữ liệu trả về theo contract với dòng dữ liệu đầy đủ trong database. Trong quá trình làm bài, tôi còn cần hỗ trợ về lệnh Git, cách pytest chọn test và việc phân biệt code Python với lệnh PowerShell. Tôi cũng cần tìm hiểu sâu hơn hai kiến trúc Single và Orchestrator để tham gia tích hợp và so sánh toàn nhóm.

- Đánh giá mức độ hoàn thành phần việc và bài học rút ra: Tôi đã hoàn thành triển khai Workflow, có 62 test student Workflow và 8 trường hợp kiểm thử bổ sung chạy thành công; crash suite đạt 20/20. Phần tích hợp và kiểm tra bài nộp toàn nhóm còn phụ thuộc vào việc bàn giao hai shape còn lại. Bài học chính là phải kiểm chứng code do AI hỗ trợ bằng test và dữ liệu thực tế, đồng thời phân biệt lỗi môi trường, lỗi test và lỗi triển khai trước khi sửa.

