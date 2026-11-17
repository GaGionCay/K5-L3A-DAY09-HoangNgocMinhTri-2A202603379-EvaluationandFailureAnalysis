# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 — Evaluation confounders |
| SOURCE | Nguồn bằng chứng cho kết quả ablation: `docs/metrics.md` (định nghĩa metrics), `src/lab8/benchmark.py` (runner/evaluator), và `src/reports/benchmark.json` (dữ liệu trial); loại bằng chứng: benchmark thực thi trong repo, không phải kết quả từ paper ngoài. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Thiết kế benchmark giữ corpus, seed, giá, evaluator và cô lập DB như nhau giữa các shape; do đó báo cáo hỗ trợ mô tả chênh lệch trên public corpus này, không tự nó chứng minh tác động nhân quả của topology. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Chỉ public corpus hiện có (14 claim × 5 seed = 70 trial/shape), `MockLLM`, ngày `as_of=2026-11-15`, bảng giá mô phỏng VND và các implementation trong snapshot benchmark. Không ngoại suy sang hidden set hay production; latency là `unavailable`. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | H1, ghi trước lần benchmark được tạo lại: khi cả hai shape hoàn chỉnh theo cùng business contract, `single` sẽ không kém `workflow` quá 5 điểm phần trăm về pass rate; `single` dự kiến tốn simulated cost/success và trace steps cao hơn do vòng ReAct. Report cũ có trước H1; chỉ lần chạy mới bên dưới dùng để đánh giá H1. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cặp so sánh `workflow` (deterministic workflow) với `single` (một ReAct agent, cap 8 bước; tool worker chỉ đọc, host duy nhất ghi refund). Cố định theo metadata: 14 claim C-001…C-014, seed 11/22/33/44/55, `MockLLM`, `as_of=2026-11-15`, pricing simulated (20 VND/1k input tokens, 80 VND/1k output tokens, 10 VND/tool call), evaluator `trial_pass`, cùng tool adapters/manifest khả dụng, fresh SQLite cho từng trial. Ghép cặp theo đúng `(claim_id, seed)`; shape là biến treatment. Các tool được gọi thực tế có thể khác theo shape. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Theo dõi paired pass/fail, pass rate, pass^5, 5 seed rates/min/max/population variance, cost/success, mean/p95 trace events, trace/leak và approval bypass. Failure mode cần kiểm soát: một shape chưa implement có thể làm chênh lệch trông như hiệu quả kiến trúc; kiểm tra status/reason và source trước khi diễn giải. Cost là mô phỏng, không phải hóa đơn API. |

## Kết quả ablation

- **Lệnh benchmark đã chạy (PowerShell, từ `src/`):** `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data\public_claims.jsonl --seeds 11,22,33,44,55 --out reports\benchmark.json`
- **Report:** `src/reports/benchmark.json`. JSON ghi `run_id` theo từng trial, không có một benchmark-level run id. Bảng dưới liệt kê đủ 70 cặp run id của `workflow` và `single`; mỗi cặp dùng chung claim và seed.
- **Kiểm soát xác nhận từ report:** 14 claim, 5 seed, 70 cặp duy nhất và không trùng; metadata ghi `MockLLM`, `as_of=2026-11-15`, simulated VND pricing và `fresh_sqlite_per_trial`. Benchmark runner gọi cùng evaluator `trial_pass` cho mọi shape.
- **Kết quả paired:** 70/70 cặp đều pass ở cả hai shape; 0 cặp discordant. Mỗi seed có 14/14 pass cho cả `workflow` và `single`; chênh lệch pass rate là 0 pp ở mọi seed. Pass^5: 14/14 (100%) cho cả hai; population variance 0, min/max 100–100%.
- **Cost / trace:** `workflow` tổng cost mô phỏng 1,950 VND, cost/success 27.86 VND, mean/p95 steps 3.79/4; `single` tổng 3,372.90 VND, cost/success 48.18 VND, mean/p95 steps 6.64/8. Chênh lệch chính xác theo số liệu chưa làm tròn là 20.33 VND/success và 2.86 trace events trung bình. Chi phí `single` bao gồm token model được tích lũy qua `MockLLM.complete`; latency `unavailable`.
- **Đối chiếu hypothesis:** H1 được hỗ trợ trên public benchmark này: `single` ngang `workflow` về pass rate (100%, chênh 0 pp, nằm trong biên không-kém-hơn 5 pp) và tốn cost/success, trace steps cao hơn. Đây là paired description trên 70 cặp, không phải chứng minh tổng quát hay đánh giá production.
- **Giới hạn / thời điểm hypothesis:** H1 được ghi trước benchmark mới; file report trước đó là kết quả lịch sử và không dùng để kiểm định H1. Các implementation hoàn tất trước lần chạy mới. Public set có 14 claim, không phải hidden 40 claim; MockLLM không phải model production; giá là mô phỏng; latency `unavailable`.

### Paired run IDs (workflow ↔ single)

| Claim | Seed: workflow run_id ↔ single run_id |
| --- | --- |
| C-001 | 11: `R-workflow-C-001-s11` ↔ `R-single-C-001-s11`; 22: `R-workflow-C-001-s22` ↔ `R-single-C-001-s22`; 33: `R-workflow-C-001-s33` ↔ `R-single-C-001-s33`; 44: `R-workflow-C-001-s44` ↔ `R-single-C-001-s44`; 55: `R-workflow-C-001-s55` ↔ `R-single-C-001-s55` |
| C-002 | 11: `R-workflow-C-002-s11` ↔ `R-single-C-002-s11`; 22: `R-workflow-C-002-s22` ↔ `R-single-C-002-s22`; 33: `R-workflow-C-002-s33` ↔ `R-single-C-002-s33`; 44: `R-workflow-C-002-s44` ↔ `R-single-C-002-s44`; 55: `R-workflow-C-002-s55` ↔ `R-single-C-002-s55` |
| C-003 | 11: `R-workflow-C-003-s11` ↔ `R-single-C-003-s11`; 22: `R-workflow-C-003-s22` ↔ `R-single-C-003-s22`; 33: `R-workflow-C-003-s33` ↔ `R-single-C-003-s33`; 44: `R-workflow-C-003-s44` ↔ `R-single-C-003-s44`; 55: `R-workflow-C-003-s55` ↔ `R-single-C-003-s55` |
| C-004 | 11: `R-workflow-C-004-s11` ↔ `R-single-C-004-s11`; 22: `R-workflow-C-004-s22` ↔ `R-single-C-004-s22`; 33: `R-workflow-C-004-s33` ↔ `R-single-C-004-s33`; 44: `R-workflow-C-004-s44` ↔ `R-single-C-004-s44`; 55: `R-workflow-C-004-s55` ↔ `R-single-C-004-s55` |
| C-005 | 11: `R-workflow-C-005-s11` ↔ `R-single-C-005-s11`; 22: `R-workflow-C-005-s22` ↔ `R-single-C-005-s22`; 33: `R-workflow-C-005-s33` ↔ `R-single-C-005-s33`; 44: `R-workflow-C-005-s44` ↔ `R-single-C-005-s44`; 55: `R-workflow-C-005-s55` ↔ `R-single-C-005-s55` |
| C-006 | 11: `R-workflow-C-006-s11` ↔ `R-single-C-006-s11`; 22: `R-workflow-C-006-s22` ↔ `R-single-C-006-s22`; 33: `R-workflow-C-006-s33` ↔ `R-single-C-006-s33`; 44: `R-workflow-C-006-s44` ↔ `R-single-C-006-s44`; 55: `R-workflow-C-006-s55` ↔ `R-single-C-006-s55` |
| C-007 | 11: `R-workflow-C-007-s11` ↔ `R-single-C-007-s11`; 22: `R-workflow-C-007-s22` ↔ `R-single-C-007-s22`; 33: `R-workflow-C-007-s33` ↔ `R-single-C-007-s33`; 44: `R-workflow-C-007-s44` ↔ `R-single-C-007-s44`; 55: `R-workflow-C-007-s55` ↔ `R-single-C-007-s55` |
| C-008 | 11: `R-workflow-C-008-s11` ↔ `R-single-C-008-s11`; 22: `R-workflow-C-008-s22` ↔ `R-single-C-008-s22`; 33: `R-workflow-C-008-s33` ↔ `R-single-C-008-s33`; 44: `R-workflow-C-008-s44` ↔ `R-single-C-008-s44`; 55: `R-workflow-C-008-s55` ↔ `R-single-C-008-s55` |
| C-009 | 11: `R-workflow-C-009-s11` ↔ `R-single-C-009-s11`; 22: `R-workflow-C-009-s22` ↔ `R-single-C-009-s22`; 33: `R-workflow-C-009-s33` ↔ `R-single-C-009-s33`; 44: `R-workflow-C-009-s44` ↔ `R-single-C-009-s44`; 55: `R-workflow-C-009-s55` ↔ `R-single-C-009-s55` |
| C-010 | 11: `R-workflow-C-010-s11` ↔ `R-single-C-010-s11`; 22: `R-workflow-C-010-s22` ↔ `R-single-C-010-s22`; 33: `R-workflow-C-010-s33` ↔ `R-single-C-010-s33`; 44: `R-workflow-C-010-s44` ↔ `R-single-C-010-s44`; 55: `R-workflow-C-010-s55` ↔ `R-single-C-010-s55` |
| C-011 | 11: `R-workflow-C-011-s11` ↔ `R-single-C-011-s11`; 22: `R-workflow-C-011-s22` ↔ `R-single-C-011-s22`; 33: `R-workflow-C-011-s33` ↔ `R-single-C-011-s33`; 44: `R-workflow-C-011-s44` ↔ `R-single-C-011-s44`; 55: `R-workflow-C-011-s55` ↔ `R-single-C-011-s55` |
| C-012 | 11: `R-workflow-C-012-s11` ↔ `R-single-C-012-s11`; 22: `R-workflow-C-012-s22` ↔ `R-single-C-012-s22`; 33: `R-workflow-C-012-s33` ↔ `R-single-C-012-s33`; 44: `R-workflow-C-012-s44` ↔ `R-single-C-012-s44`; 55: `R-workflow-C-012-s55` ↔ `R-single-C-012-s55` |
| C-013 | 11: `R-workflow-C-013-s11` ↔ `R-single-C-013-s11`; 22: `R-workflow-C-013-s22` ↔ `R-single-C-013-s22`; 33: `R-workflow-C-013-s33` ↔ `R-single-C-013-s33`; 44: `R-workflow-C-013-s44` ↔ `R-single-C-013-s44`; 55: `R-workflow-C-013-s55` ↔ `R-single-C-013-s55` |
| C-014 | 11: `R-workflow-C-014-s11` ↔ `R-single-C-014-s11`; 22: `R-workflow-C-014-s22` ↔ `R-single-C-014-s22`; 33: `R-workflow-C-014-s33` ↔ `R-single-C-014-s33`; 44: `R-workflow-C-014-s44` ↔ `R-single-C-014-s44`; 55: `R-workflow-C-014-s55` ↔ `R-single-C-014-s55` |

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
