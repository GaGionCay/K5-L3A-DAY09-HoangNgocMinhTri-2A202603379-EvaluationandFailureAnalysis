# Team

## Thông tin nhóm

- Tên nhóm: CAT
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-CAT-FromWorkflowsToAgents`
- URL repo: https://github.com/GaGionCay/K5-L3A-DAY08-CAT-FromWorkflowsToAgents
- Nhánh nộp: `main`.
- Commit chốt: `33267fa`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Nguyễn Thế Cường | 2A202603355 | 26ai.cuongnt2@vinuni.edu.vn | Chill2004 | Workflow; tích hợp; kiểm thử crash; checklist nộp bài |
| 2 | Hoàng Ngọc Minh Trí | 2A202603379 | 26ai.trihnm@vinuni.edu.vn | GaGionCay | Shape B (single), benchmark/evaluation, research card |
| 3 | Chử Thị Ánh | 2A202603360 | 26ai.anhct@vinuni.edu.vn | chuanh1214 | Orchestrator, kiểm handoff, quyền tool và trace; chủ trì tổng hợp báo cáo nhóm |

## Phân công và phối hợp

| Người | Phần triển khai | Sản phẩm và trách nhiệm |
| --- | --- | --- |
| Cường | `src/lab8/shapes/workflow.py` | Luồng Python cố định; test riêng trong `src/tests/test_workflow.py`; chạy crash suite; tích hợp và kiểm tra hồ sơ nộp |
| Hoàng Ngọc Minh Trí | `src/lab8/shapes/single.py` | Vòng ReAct tối đa 8 bước, model chỉ chọn tool đọc; test riêng; benchmark 4 shape với seed quy định; tổng hợp metric và research card |
| Ánh | `src/lab8/shapes/orchestrator.py` | Orchestrator và investigator chỉ đọc; handoff qua allowlist; test riêng; rà trace và tổng hợp báo cáo nhóm |

- Mỗi người chịu trách nhiệm contract kết quả, quote đầy đủ, approval, trace và crash trong shape mình viết; không sửa host hoặc thước đo có sẵn.
- Swarm có sẵn được dùng làm đối chứng, không phân công viết lại.
- Cả nhóm chọn kiến trúc từ số liệu, hoàn thiện ADR và ablation; người tổng hợp báo cáo không thay thế trách nhiệm báo cáo cá nhân.
- Mỗi thành viên phải có commit kỹ thuật và ít nhất một test thêm/sửa trên nhánh nộp, rồi tự nộp cùng link repo nhóm trên LMS.

## Bảng đóng góp

Giữ nguyên tiêu đề và các cột để `python -m lab8.check_submission` đọc. Chỉ ghi hash thật; các phần chưa commit hoặc chưa bàn giao được đánh dấu rõ bên dưới.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Thế Cường | Workflow; test hồi quy; kiểm thử crash | `b75d072` (triển khai Workflow); `8ede40e` (test, báo cáo cá nhân và crash report); `1b2c4af` (cập nhật báo cáo cá nhân trên nhánh ntc) | `src/tests/test_workflow.py`: 7 hàm, 8 trường hợp chạy, đã nằm trong commit `8ede40e`; kiểm tra ticket injection, thiếu order_id, rò secret, approval hết hạn, cap theo approval, approval sai claim và crash/resume/retry; kết quả 8 passed |
| Hoàng Ngọc Minh Trí (2A202603379) | Shape B (single), benchmark/evaluation, research card | `8c67fde` | `src/tests/test_react_step_cap.py::test_react_stops_at_step_cap` (added); `src/tests/test_public_matrix.py` (62 Shape B cases passed) |
| Chử Thị Ánh (2A202603360) | Orchestrator; handoff; trace; tổng hợp báo cáo nhóm | `0d3fa46` | `src/tests/test_orchestrator_contract.py`: 4 test passed; toàn bộ test student 248 passed; kiểm tra handoff allowlist, chặn write tool, trace có `run_id`, không chứa secret/PII/`parent_secret`, và crash được truyền xuống `issue_refund` |

## Cá nhân

Mỗi người copy mẫu `report/team/MSSV_HoTen.md` thành file riêng theo MSSV và họ tên không dấu; giữ lại file mẫu. Ghi công cụ AI đã dùng và cách tự kiểm chứng.

### Nguyễn Thế Cường — 2A202603355

- Báo cáo: [2A202603355_NguyenTheCuong.md](report/team/2A202603355_NguyenTheCuong.md).
- Nhánh cá nhân: `ntc`.
- Đã triển khai Workflow, truyền quote đầy đủ và `crash_at` vào host, không bắt `InjectedCrash`; mọi nhánh trả kết quả qua `finish()`.
- Test bổ sung: chống chỉ dẫn trong ticket (2 seed); không suy mã đơn từ ticket; không lộ token trong output; retry với approval hết hạn; cap theo approval và retry; approval sai claim; crash → resume → retry 3 lần.
- Kết quả đã xác nhận: 62 test student Workflow; 8 trường hợp test bổ sung; lệnh test mặc định 62 passed, 248 deselected; crash suite 20/20.
- 8 test bổ sung đã nằm trong 62 test mặc định, không cộng hai số này. Bộ 62 test student Workflow là phạm vi riêng.
- Bằng chứng crash: `src/reports/crash.json`. Trace cục bộ `R-workflow-C-001-s11` đã kiểm tra; không commit trace hoặc SQLite.
- Còn cần hoàn tất: tự đánh giá cá nhân; commit test/báo cáo và cập nhật hash; nhiệm vụ tích hợp sau khi nhận hai shape còn lại. Trạng thái push commit Workflow cần đối chiếu remote trước khi chốt bài.

