# Báo cáo cá nhân — Hoàng Ngọc Minh Trí

## 1. Thông tin thành viên

- Họ tên: Hoàng Ngọc Minh Trí
- MSSV: 2A202603379
- Email: 26ai.trihnm@vinuni.edu.vn
- GitHub: https://github.com/GaGionCay

## 2. Phần việc phụ trách

- **Shape B — ReAct Path:** triển khai `src/lab8/shapes/single.py` với claim view an toàn, worker chỉ được gọi read-only tools, giới hạn tối đa 8 bước, và chỉ host code được phép phát hành refund sau khi kiểm tra quote. Để lỗi crash được truyền theo durability contract.
- **Benchmark và phân tích:** chạy benchmark bốn shape trên cùng public corpus và năm seed; tổng hợp pass rate, pass^5, seed variance, simulated cost và trace steps.
- **Nghiên cứu:** viết research card cho paired ablation `workflow` so với `single`, nêu treatment, biến kiểm soát, metrics, giới hạn và bằng chứng theo từng run.

## 3. Đóng góp cụ thể

- **Commit chính:** [`8c67fde767d81c64efb829398b6084e44e4dd7ad`](https://github.com/GaGionCay/K5-L3A-DAY08-CAT-FromWorkflowsToAgents/commit/8c67fde767d81c64efb829398b6084e44e4dd7ad) — `feat: completed idividuals assigned task by Hoang Ngoc Minh Tri`.
- **Đóng góp mã và kiểm thử:**
  - Hoàn thiện `single.py` cho Shape B và bổ sung test giới hạn ReAct tại `test_react_stops_at_step_cap`.
  - Ghi nhận model calls, input/output tokens và simulated model cost qua `MockLLM.complete`; bổ sung `test_single_budget.py`.
  - Thêm công cụ tổng hợp benchmark và test tương ứng; cập nhật báo cáo benchmark, research card và decision record.
- **Quyết định kỹ thuật:** chọn `single` làm kiến trúc tiếp theo dựa trên kết quả benchmark: pass rate `1.000`, pass^5 `1.000`, và crash safety `20/20`. Đây không phải shape có chi phí thấp nhất; lựa chọn được giới hạn trong public benchmark và chi phí mô phỏng.

## 4. Bằng chứng

- **Benchmark:** [`benchmark.json`](../../src/reports/benchmark.json) — bốn shape, 14 claims × 5 seeds; `workflow` và `single` có 70 cặp trial. `single` đạt 70/70 pass, 100% ở từng seed, cost/success `48.18` simulated VND và mean/p95 trace steps `6.64/8`.
- **Paired run IDs:** [research card](./research_card.md) liệt kê đầy đủ run IDs theo claim và seed; ví dụ `R-workflow-C-001-s11` ↔ `R-single-C-001-s11`.
- **Crash test:** [`crash.json`](../../src/reports/crash.json) — 20/20.
- **Kiểm thử:** Shape B public cases 62/62; toàn bộ student suite 248 passed; full default pytest 69 passed (248 student cases deselected); hai regression tests của ReAct 2/2. Regression tests gồm [`test_react_stops_at_step_cap`](../../src/tests/test_react_step_cap.py) và [`test_single_budget_tracks_mock_llm_tokens_and_cost`](../../src/tests/test_single_budget.py).
- **Submission check:** `python -m lab8.check_submission` trả về `0 FAIL, 1 WARN`; warning duy nhất là các thay đổi hiện tại chưa commit (`HEAD 215a77f`).

## 5. Công cụ AI đã dùng

- **VS Code Copilot / AI assistant:** hỗ trợ triển khai và rà soát cấu trúc ReAct, điều tra tính toán budget, soạn phân tích benchmark và định dạng báo cáo.
- **Tự xác minh:** chạy pytest cho regression và public matrix, chạy `python -m lab8.benchmark`, kiểm tra kết quả bằng analyzer, rồi chạy `python -m lab8.check_submission`. Kết quả benchmark được đối chiếu trực tiếp với JSON report trước khi ghi vào research card/decision record; xem [RULES.md](../../RULES.md).

## 6. Tự đánh giá

Đã hoàn thành một ReAct agent có giới hạn rõ ràng, tách biệt quyền đọc của worker và quyền ghi của host, đồng thời bảo toàn xử lý crash theo durability contract. Kết quả được kiểm chứng bằng test, benchmark ghép cặp và crash report. Các kết luận chỉ áp dụng cho public corpus, MockLLM và simulated pricing hiện tại; chưa đại diện cho hidden workload hoặc chi phí/latency production.
