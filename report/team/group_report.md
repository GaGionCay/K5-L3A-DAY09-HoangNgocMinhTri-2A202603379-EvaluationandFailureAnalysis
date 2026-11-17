# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: CAT
- Lớp: L3A
- Repo: `https://github.com/GaGionCay/K5-L3A-DAY08-CAT-FromWorkflowsToAgents`
- Thành viên: Nguyễn Thế Cường, Hoàng Ngọc Minh Trí, Chử Thị Ánh.
- Commit chốt: `33267fa`.

## 2. Mục tiêu và cách tiếp cận

Nhóm xây dựng và đánh giá bốn cách xử lý cùng một bài toán hoàn tiền LogiX-VN:

1. `workflow`: workflow xác định, không sử dụng model để điều khiển luồng.
2. `single`: một ReAct agent có giới hạn tối đa 8 bước.
3. `orchestrator`: orchestrator điều phối các investigator chỉ đọc, còn thao tác ghi refund thuộc host.
4. `swarm`: shape tham chiếu có sẵn dùng làm đối chứng.

Mục tiêu của nhóm là giữ nguyên business contract, approval, idempotency, trace contract và crash safety giữa các shape. Mỗi trial sử dụng một claim, một seed và một SQLite database riêng. Bộ benchmark dùng 14 claim công khai với 5 seed `11, 22, 33, 44, 55`, tương ứng 70 trial cho mỗi shape.

Phân công:

- Nguyễn Thế Cường: workflow, test hồi quy, crash suite và tích hợp.
- Hoàng Ngọc Minh Trí: single agent, benchmark, evaluation và research card.
- Chử Thị Ánh: orchestrator, handoff, quyền tool, trace và tổng hợp báo cáo nhóm.

## 3. Giải pháp

### Workflow

Workflow đọc claim, order, policy và approval bằng các tool được định nghĩa sẵn. Logic quyết định được viết cố định trong Python. Workflow tính quote, kiểm tra approval và gọi `issue_refund` ở host. Model không có quyền tự chọn write tool.

### Single

Shape `single` sử dụng vòng ReAct tối đa 8 bước. Model chỉ được chọn read-only tools như lookup order, lookup policy và compute compensation. Việc ghi refund vẫn do host thực hiện sau khi quote và approval đã được kiểm tra. Step cap giúp giới hạn chi phí và tránh vòng lặp vô hạn.

### Orchestrator

Orchestrator tạo handoff theo contract `handoff.v1`. Handoff chỉ chứa các field nằm trong allowlist và chỉ cấp các tool:

- `lookup_order`
- `lookup_policy`
- `compute_compensation`

Investigator không được nhận `issue_refund` hoặc `append_audit`. Các write operation chỉ được gọi ở host thông qua `issue_refund`.

Handoff loại bỏ `parent_secret`, `raw_headers` và các field không nằm trong contract. Trace ghi các event cần cho kiểm toán như `handoff`, `investigator`, `quote`, `decision` và `crash`, nhưng không ghi raw claim row, secret, header, principal ID hoặc nội dung ticket nguyên bản.

Orchestrator truyền `crash_at` xuống `issue_refund` và để `InjectedCrash` propagate để crash suite kiểm tra đúng cửa sổ crash.

### Ranh giới code và model

- Model chỉ được đề xuất read-only action trong các shape có model.
- Host kiểm soát approval, quote, quyền ghi và idempotency.
- `issue_refund` không được expose cho investigator.
- Trace được sinh từ dữ liệu đã được sanitize.
- Handoff không được xem là cơ chế bảo mật duy nhất; allowlist được kiểm tra trực tiếp trong code.

## 4. Kết quả

Benchmark lấy từ `src/reports/benchmark.json`, gồm 14 claim × 5 seed = 70 trial cho mỗi shape.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND) | Mean/P95 steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow | 100.00% | 100.00% | 100%–100% | 0.000000 | 27.86 | 3.79 / 4 |
| single | 100.00% | 100.00% | 100%–100% | 0.000000 | 48.18 | 6.64 / 8 |
| orchestrator | 100.00% | 100.00% | 100%–100% | 0.000000 | 46.43 | 3.71 / 4 |
| swarm | 98.57% | 92.86% | 92.86%–100% | 0.000816 | 49.57 | 2.80 / 3 |

`workflow`, `single` và `orchestrator` đều đạt 70/70 trial. `swarm` đạt 69/70; một trial sai status ở seed 55.

Workflow có chi phí thấp nhất. Single có thêm chi phí model và số bước cao hơn nhưng vẫn đạt pass rate tuyệt đối. Orchestrator cũng đạt 70/70; cost/success thấp hơn single một chút nhưng cao hơn workflow. Swarm có ít bước hơn nhưng kém ổn định hơn trên trial có seed 55.

Crash safety lấy từ `src/reports/crash.json` là `20/20`.

Các test riêng của Orchestrator trong `src/tests/test_orchestrator_contract.py` đạt `4 passed`.

Toàn bộ test hiện tại:

- Test mặc định: `69 passed, 248 deselected`.
- Test student: `248 passed, 69 deselected`.
- Crash suite: `20/20`.

Các test riêng kiểm tra:

- Handoff chỉ có field hợp lệ.
- `parent_secret` không xuất hiện trong handoff.
- Investigator không được gọi write tool.
- Trace có `run_id` đúng.
- Trace không chứa secret hoặc PII.
- Crash được truyền xuống `issue_refund`.

Quyết định kiến trúc được ghi trong [decision_adr.md](./decision_adr.md). Phương pháp benchmark, hypothesis và ablation được ghi trong [research_card.md](./research_card.md).

## 5. Khó khăn và cách xử lý

### Rò rỉ secret và dữ liệu nhạy cảm

Claim chứa `parent_secret`, raw authorization header và nội dung ticket. Nhóm xử lý bằng allowlist ở handoff, các tool trả về field giới hạn và trace chỉ ghi dữ liệu cần thiết. Test sử dụng canary secret để phát hiện việc lộ dữ liệu.

### Investigator gọi write tool

Investigator có thể bị yêu cầu gọi nhầm `issue_refund`. Nhóm xử lý bằng hai lớp kiểm soát: handoff chỉ cho phép read-only tools và runtime từ chối write tools khi `worker=True`.

### Crash giữa effect và checkpoint

Nhóm kiểm tra cửa sổ `after_effect_before_checkpoint`. Orchestrator truyền `crash_at` xuống `issue_refund`, không bắt hoặc che giấu `InjectedCrash`. Cơ chế idempotency và retry bảo đảm không tạo refund trùng.

### Khác biệt giữa các shape

Nhóm cố định claim, seed, model backend, tool manifest, pricing, evaluator và SQLite isolation. Benchmark ghép cặp theo cùng `(claim_id, seed)` để giảm ảnh hưởng của các biến ngoài topology.

## 6. Tổng hợp đóng góp

Chi tiết từng thành viên được ghi trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân.

- Nguyễn Thế Cường triển khai workflow, bổ sung các test về prompt injection, approval, retry, idempotency và crash.
- Hoàng Ngọc Minh Trí triển khai single ReAct agent, benchmark, evaluation và research card.
- Chử Thị Ánh triển khai orchestrator, handoff allowlist, quyền read-only của investigator, trace contract và test riêng cho Orchestrator.
- Cả nhóm chạy benchmark bốn shape, crash suite và rà soát hồ sơ nộp bài.

## 7. Hạn chế và hướng cải thiện

- Benchmark chỉ dùng 14 claim công khai × 5 seed, không đại diện đầy đủ cho hidden set.
- `MockLLM` không phải model production.
- Chi phí là simulated VND, không phải hóa đơn API thực tế.
- Latency hiện là `unavailable`.
- Kết quả không chứng minh rằng topology là nguyên nhân duy nhất của chênh lệch nếu prompt, tool hoặc implementation thay đổi.
- Orchestrator đạt pass rate tuyệt đối; cost/success cao hơn workflow nhưng thấp hơn single một chút trong public benchmark.
- Handoff và trace hiện được kiểm tra bằng contract test; production cần bổ sung schema validation, access control, audit storage và policy kiểm duyệt PII.
- Cần chạy lại benchmark trên hidden workload hoặc corpus lớn hơn trước khi kết luận về production.

## 8. Tài liệu tham khảo

- [TEAM.md](../../TEAM.md)
- [docs/architecture.md](../../docs/architecture.md)
- [docs/contracts.md](../../docs/contracts.md)
- [docs/business_rules.md](../../docs/business_rules.md)
- [report/team/decision_adr.md](./decision_adr.md)
- [report/team/research_card.md](./research_card.md)
- [src/reports/benchmark.json](../../src/reports/benchmark.json)
- [src/reports/crash.json](../../src/reports/crash.json)
- Yao et al., 2022, ReAct: Synergizing Reasoning and Acting in Language Models: https://arxiv.org/abs/2210.03629