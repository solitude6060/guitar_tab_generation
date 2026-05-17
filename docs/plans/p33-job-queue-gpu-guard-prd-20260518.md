# P33 Job Queue + GPU Resource Guard PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P33 建立本機 job queue 與 GPU resource guard，讓 3-8 分鐘的 heavy tasks 可以被排程、取消、恢復並留下 logs，同時保護共享 RTX 4090。

交付：

- 新增 CLI：`guitar-tab-generation jobs <submit|status|run-next|cancel|resume>`。
- workspace 內建立 `.gtg_jobs/queue.json` 與 `.gtg_jobs/logs/<job_id>.log`。
- GPU-sensitive job 必須明確 opt-in；預設不使用 GPU、不 probe GPU。
- `run-next` 對 GPU job enforce one-GPU-task-at-a-time lock。
- VRAM 不足或 GPU lock 已存在時，job 進入 deferred 並保留 reason/log evidence。

## 2. 非目標

- 不建立背景 daemon。
- 不執行真實 Demucs / Basic Pitch / LLM heavy runtime。
- 不下載模型、不佔用 GPU 作為 default CI。
- 不取代既有 artifact CLI；queue 只保存工作規格與狀態。

## 3. 使用者流程

```bash
guitar-tab-generation jobs submit /path/to/workspace --job-id demo --command transcribe --command song.wav --command --backend --command fixture
guitar-tab-generation jobs status /path/to/workspace
guitar-tab-generation jobs run-next /path/to/workspace
guitar-tab-generation jobs cancel /path/to/workspace demo
guitar-tab-generation jobs resume /path/to/workspace demo
```

GPU job：

```bash
guitar-tab-generation jobs submit /path/to/workspace --job-id stems --gpu --allow-gpu --command separate-stems --command song
guitar-tab-generation jobs run-next /path/to/workspace --allow-gpu --min-free-vram-mb 12000
```

## 4. 驗收標準

- Queue ordering deterministic。
- GPU job 沒有 opt-in 時不能 submit / run。
- GPU lock 已存在時，下一個 GPU job deferred。
- 低 VRAM 時 GPU job deferred，並寫入 reason。
- cancel/resume 會更新 queue state 與 log。
- `jobs --help` 與各 subcommand help 可用。
