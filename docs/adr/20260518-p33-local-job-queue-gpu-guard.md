# ADR: P33 Local Job Queue and GPU Guard

日期：2026-05-18
狀態：Accepted

## Context

v1.0 MVP 需要排程長任務並保護共享 RTX 4090，但 default CI 與一般 CLI 預設不得佔用 GPU、下載模型或執行真實 heavy runtime。

## Decision

P33 使用 repo-local stdlib implementation：

- 每個 workspace 以 `.gtg_jobs/queue.json` 保存 job records。
- 每個 job 以 `.gtg_jobs/logs/<job_id>.log` 保存事件。
- GPU mutual exclusion 使用 `.gtg_jobs/gpu.lock`。
- CLI `jobs run-next` 只模擬 lifecycle，不直接執行 command；後續 P38/P39 可把 queue 接到 service boundary。
- GPU-sensitive job 需要 submit-time `--allow-gpu` opt-in，run-time 仍需 `--allow-gpu` 才能 probe VRAM / acquire lock。
- Tests 使用 fake VRAM probe / `--fake-free-vram-mb`，不要求 default CI 有 GPU。

## Rejected

- Background daemon：超出 P33，會引入 lifecycle 與 shutdown complexity。
- SQLite：目前 queue record 小且單機，JSON 足以支援 MVP；P38 若需要 multi-project concurrency 再評估。
- Shell execution：會把 queue 與 pipeline execution 綁太緊，也提高安全風險；P33 先保存 command spec 與 lifecycle evidence。

## Consequences

- Queue 是本機單程序最佳努力，不保證跨程序 transaction。
- GPU lock 是檔案鎖語意的最小可驗版本；真 worker daemon 應在 P39 前重新評估 crash recovery。
