# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: single
- Commit hash: `33267fa`
- Run id dẫn chứng: `R-single-C-001-s11`
- Pass rate / pass^5 / seed min-max / variance: `1.000 / 1.000 / 1.000–1.000 / 0.000000` (70 trials, 14 claims × 5 seeds)
- Cost per success (mô phỏng, VND): `48.18` (total simulated cost `3,372.90`)
- Crash safety: `20/20` (`src/reports/crash.json`)
- Secret leak / approval bypass: `0 / 0` observed on the 70-trial public set; all trials passed the evaluator's leak and approval checks.

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Chọn `single` để mang Shape B — một bounded ReAct agent — qua evaluation tiếp theo. Trên cùng 14 public claim và 5 seed, `single` đạt 70/70 pass và pass^5 14/14; mỗi seed đều đạt 14/14. Đây không phải lựa chọn tiết kiệm nhất: `workflow` cũng đạt 70/70 nhưng tốn 27.86 simulated VND/success so với 48.18 của `single`; `single` có thêm 2.86 trace events trung bình. Nhóm giữ `single` vì mục tiêu đánh giá ReAct path, không phải vì ưu thế về chi phí. Chi phí `single` bao gồm token model được tính bằng `MockLLM.complete`. Nếu ưu tiên giảm cost trong benchmark hiện tại, `workflow` là lựa chọn hợp lý hơn.

## Có đáng đổi lấy multi-agent không

Trên benchmark mới, `orchestrator` đạt cùng pass rate `1.000` nhưng cost/success thấp hơn một chút (`46.43` so với `48.18` VND) và không cải thiện pass^5 so với `single`; `swarm` pass rate là `0.986` và pass^5 là `0.929`. Vì vậy lựa chọn `single` không được diễn giải là tốt hơn về hiệu quả chi phí; đây là lựa chọn tiếp tục kiểm thử ReAct. Xem xét lại nếu mục tiêu tối ưu là chi phí hoặc hidden workload cho thấy khác biệt về pass/robustness.

## Trace và bằng chứng

`single` trace ghi `claim_view`, các lựa chọn read-tool, quote đã tính, thao tác host refund và kết quả refund. Trace không ghi ticket, parent secret/header, claim row hoặc raw order row; chỉ ghi trạng thái và dữ kiện tối thiểu cần cho kiểm toán. Bằng chứng: `src/reports/benchmark.json`, các run ID theo trial ở `report/team/research_card.md`, và trace contract/leak checks trong evaluator. Trace ở thư mục `src/traces/`, trong phạm vi scanner của grader.

## Giới hạn

Public benchmark có 14 claim × 5 seed và không đại diện cho hidden 40-claim set. Giá là mô phỏng, không phải hóa đơn API; MockLLM không phải model sản xuất; latency là `unavailable`. Không suy rộng kết quả này thành đảm bảo về production.
