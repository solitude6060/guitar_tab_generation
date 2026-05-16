# 剩餘功能總規劃（P21–P40）

日期：2026-05-16
狀態：Planned
適用範圍：`guitar_tab_generation` P20 之後的完整產品化路線
原則：嚴格 SDD / TDD / planning with files / git dev flow / uv-first / `.omx` local-only

## 1. 目前基準線

已完成到 P20：

- 合法本機音訊輸入與 normalized WAV artifact。
- 3–8 分鐘 full-song 長度支援與 chunk planning。
- Basic Pitch 真實 note transcription backend（explicit `--backend basic-pitch`）。
- TAB / viewer / tutorial / offline interface。
- MIDI / MusicXML / DAW bundle 匯出。
- Docker Compose dev/gpu-ai/llm/cloud-backup profiles。
- 本機 AI backend registry、model smoke、Torch-first route registry。
- `f0-calibrate` sidecar：讀 `audio_normalized.wav` + `notes.json`，輸出 `f0_calibration.json`。

目前刻意未做：

- 任意 YouTube / URL 自動下載。
- 真實 source separation。
- 真實 chord recognition。
- 真實 section detection。
- 完整 Web App。
- 直接產生 `.band` / Logic project。
- 自動安裝 PyTorch / Demucs / torchcrepe heavy dependencies。

## 2. 產品完成目標分層

### 2.1 MVP+（P21–P27）

目標：把已存在 artifact 與 AI sidecar 串成可用工作流。

- F0 calibration 結果可被 viewer/interface/tutorial 消費。
- optional Torch dependency groups 與 GPU smoke 可重現。
- torchcrepe 真實 runtime 可 opt-in 跑通。
- Demucs stem separation 進入 artifact-first sidecar。
- Basic Pitch + F0 + stems 形成第一版可用 AI pipeline。

### 2.2 Beta（P28–P34）

目標：從 CLI 工具變成可使用產品。

- Web UI / job queue / artifact browser。
- 更準確的 chord / section / fingering。
- QA eval dataset 與 regression scoring。
- 本機 LLM 教學強化。
- 合法 URL policy path 完整化。

### 2.3 v1.0（P35–P40）

目標：產品化與可維護性。

- GPU resource scheduler。
- model cache manager。
- export quality hardening。
- user project workspace。
- packaged local app / Docker Compose stable profiles。
- documentation + demo assets。

## 3. 剩餘 Epic 總表

| Priority | Epic | 目標 | 建議分支 | 狀態 |
|---|---|---|---|---|
| P21 | F0 Calibration Consumption | viewer/interface/tutorial 顯示 `f0_calibration.json` 低信心音符 | `feature/f0-calibration-consumption` | Planned |
| P22 | Optional Torch Dependency Group | 新增可選 `torch` dependency group 與安裝文件，不影響 dev default | `feature/optional-torch-deps` | Planned |
| P23 | Real torchcrepe Runtime Smoke | 在 opt-in 環境跑真實 torchcrepe CPU/GPU smoke | `feature/real-torchcrepe-smoke` | Planned |
| P24 | Demucs Runtime Planning + Install Gate | Demucs optional dependency / cache / GPU gate 規格化 | `feature/demucs-runtime-gate` | Planned |
| P25 | Demucs Stem Separation Sidecar | `separate-stems` 產生 stems artifact，不改 transcribe default | `feature/demucs-stem-sidecar` | Planned |
| P26 | Stem-aware Basic Pitch Pipeline | 可選對 guitar stem 跑 Basic Pitch，提高 notes cleanliness | `feature/stem-aware-basic-pitch` | Planned |
| P27 | Artifact Quality Scoring v2 | 合併 Basic Pitch/F0/stem confidence，產生更實用 quality report | `feature/artifact-quality-v2` | Planned |
| P28 | Chord Recognition Backend | 新增真實 chord estimation sidecar / backend | `feature/chord-recognition-backend` | Planned |
| P29 | Section Detection Backend | 新增真實 section/structure detection sidecar / backend | `feature/section-detection-backend` | Planned |
| P30 | Fingering + Playability v2 | solo/riff 指法推定與可彈性修正 | `feature/fingering-playability-v2` | Planned |
| P31 | Local LLM Tutorial v2 | 用本機 LLM 基於 artifacts 產生更完整教學，不作 truth source | `feature/local-llm-tutorial-v2` | Planned |
| P32 | Web UI MVP | artifact-first Web UI：上傳、本機 job、結果瀏覽 | `feature/web-ui-mvp` | Planned |
| P33 | Job Queue + GPU Resource Guard | 排程長任務，保護共享 RTX 4090 | `feature/job-queue-gpu-guard` | Planned |
| P34 | Legal URL / YouTube Path | 僅在明確權利/本機工具/政策 gate 下支援 URL flow | `feature/legal-url-path` | Planned |
| P35 | Evaluation Dataset + Metrics | 建立 fixture/eval set 與 transcription quality metrics | `feature/eval-dataset-metrics` | Planned |
| P36 | DAW Export Quality v2 | tempo map / markers / track naming / manifest hardening | `feature/daw-export-quality-v2` | Planned |
| P37 | Model Cache Manager | 管理模型 cache、版本、磁碟使用與 smoke evidence | `feature/model-cache-manager` | Planned |
| P38 | Project Workspace | 多歌曲 workspace、history、artifact index | `feature/project-workspace` | Planned |
| P39 | Packaged Local App | Docker Compose stable / local app packaging / setup wizard | `feature/packaged-local-app` | Planned |
| P40 | v1.0 Release Hardening | docs、demo、CI gates、security/legal final review | `release/v1.0-hardening` | Planned |

## 4. 逐階段規格摘要

### P21：F0 Calibration Consumption

目標：讓 `f0_calibration.json` 不只是 sidecar，而是被產品介面使用。

交付：

- `view` 顯示 F0 calibration summary。
- `interface.html` 顯示 pitch-risk notes 與 `delta_semitones`。
- `tutorial.md` 將低 confidence / 大偏差音符列為練習重點。

測試：

- Unit：artifact reader 可解析 `f0_calibration.json`。
- E2E：fixture artifact + fake calibration → viewer/interface/tutorial 都顯示 pitch risk。

### P22：Optional Torch Dependency Group

目標：建立可重現但不強迫的 Torch 環境。

交付：

- `pyproject.toml` 新增 optional group，例如 `torch-ai`。
- 文件明確區分 default dev、Basic Pitch ai、Torch ai。
- 不在 CI default 跑 Torch heavy tests。

依賴策略：

- 只加入 P23/P25 確定會直接呼叫的 package。
- 若 `torchcrepe` 需要 PyTorch variant，優先文件化 CPU/GPU wheel 選項，不硬塞單一 CUDA wheel。

測試：

- lock / help / import-optional checks。
- 不要求 CI 安裝 Torch group。

### P23：Real torchcrepe Runtime Smoke

目標：真實跑通 `f0-calibrate` 的 torchcrepe runtime。

交付：

- `torch-smoke --route torchcrepe-f0 --run` 可執行真實 import smoke。
- CPU smoke 使用短 fixture，輸出 `f0_calibration.json`。
- GPU smoke 只有 VRAM gate 通過且明確 opt-in 才跑。

測試：

- Unit：runtime command builder。
- Manual gate：CPU real smoke。
- Optional GPU gate：`GPU_TESTS_ENABLED=1`。

### P24：Demucs Runtime Planning + Install Gate

目標：在真正做 stem separation 前，把資源、cache、錯誤與跳過策略定清楚。

交付：

- Demucs PRD / ADR。
- `demucs-htdemucs` cache / model path / GPU gate 文件。
- no-auto-download default。

測試：

- GPU insufficient → skip。
- missing demucs → clear error。
- no silent fallback。

### P25：Demucs Stem Separation Sidecar

目標：新增：

```bash
guitar-tab-generation separate-stems <artifact_dir>
```

交付：

- 輸出 `stems/`、`stem_manifest.json`。
- 不改 `transcribe` default。
- 預設不跑 GPU，除非明確 opt-in。

測試：

- fake demucs runtime unit tests。
- E2E sidecar artifact contract。

### P26：Stem-aware Basic Pitch Pipeline

目標：允許 Basic Pitch 對 guitar stem 執行，改善 notes cleanliness。

交付：

- `transcribe --backend basic-pitch --stem guitar` 或 sidecar merge path。
- provenance 標記 `stem=guitar`。
- 若 stems 不存在，清楚提示先跑 `separate-stems`。

測試：

- stem path selection。
- provenance contract。
- no fallback to mix silently。

### P27：Artifact Quality Scoring v2

目標：把 notes / F0 / stems / warnings 合成更實用的 quality report。

交付：

- `quality_report.json` v2 schema。
- pitch risk、stem availability、backend confidence summary。
- viewer/interface 顯示 quality summary。

測試：

- schema unit tests。
- regression snapshots。

### P28：Chord Recognition Backend

目標：新增真實 chord recognition sidecar 或 backend。

候選：

- Essentia/chroma-based local feature route。
- Basic Pitch notes → chord inference baseline。
- 後續再評估 Torch chord model。

交付：

- `chord-detect <artifact_dir>` sidecar。
- `chords.json` provenance 升級。

測試：

- deterministic fixture chord expectations。
- low-confidence warnings。

### P29：Section Detection Backend

目標：產生更可信的 verse/chorus/solo/bridge sections。

交付：

- `section-detect <artifact_dir>` sidecar。
- novelty / repetition baseline。
- interface 顯示 section confidence。

測試：

- fixture section boundaries。
- full-song chunk boundaries。

### P30：Fingering + Playability v2

目標：把 solo / riff notes 轉成更合理 TAB 指法。

交付：

- fingering DP / cost model。
- position shift / string preference / max stretch config。
- low confidence fingering warnings。

測試：

- known riff golden snapshots。
- impossible stretch warnings。

### P31：Local LLM Tutorial v2

目標：用本機 LLM 強化教學文字，但永遠只基於 artifacts，不當 notes/chords truth source。

交付：

- `tutorial --llm local`。
- prompt artifact log。
- fallback to deterministic tutorial when LLM missing。

測試：

- prompt builder unit tests。
- fake LLM e2e。
- policy：LLM 不改 notes/chords。

### P32：Web UI MVP

目標：從 CLI artifact viewer 進化為本機 Web UI。

交付：

- Upload local audio。
- Job status。
- Artifact browser。
- TAB / quality / DAW / tutorial tabs。

限制：

- UI 不重寫 pipeline。
- UI 呼叫 CLI/service boundary。

測試：

- API contract tests。
- Playwright e2e。

### P33：Job Queue + GPU Resource Guard

目標：保護共享 GPU 並管理 3–8 分鐘任務。

交付：

- job queue。
- VRAM guard。
- one-GPU-task-at-a-time lock。
- cancel / resume / logs。

測試：

- queue ordering。
- GPU busy skip/defer。
- job artifact lifecycle。

### P34：Legal URL / YouTube Path

目標：回應原始 YouTube URL 需求，但不能開任意下載。

交付：

- ADR 更新：合法來源與權利聲明。
- `ingest-url` policy gate。
- 只允許使用者明確提供權利聲明、且本機工具存在時執行。
- 所有 URL artifact 留下 source policy record。

測試：

- no-rights → blocked。
- unsupported URL → blocked。
- local-owned sample URL fixture → allowed via stub。

### P35：Evaluation Dataset + Metrics

目標：建立可量化品質，而不是只靠 demo 感覺。

交付：

- eval fixtures manifest。
- note onset/pitch/chord/section metrics。
- regression report。

測試：

- metric unit tests。
- baseline threshold gate。

### P36：DAW Export Quality v2

目標：讓 GarageBand / Logic 匯入體驗更接近成品。

交付：

- tempo map。
- markers / sections。
- track naming。
- manifest versioning。
- import checklist validation。

測試：

- DAW manifest schema。
- MIDI/MusicXML track count / marker tests。

### P37：Model Cache Manager

目標：管理本機模型、版本、cache size 與 smoke evidence。

交付：

- `models list`
- `models doctor`
- `models prune --dry-run`
- model manifest。

測試：

- dry-run no destructive action。
- cache discovery fixtures。

### P38：Project Workspace

目標：支援多歌曲、多版本 artifacts。

交付：

- workspace index。
- song/project metadata。
- artifact history。
- interface project list。

測試：

- index update。
- multiple artifact dirs。

### P39：Packaged Local App

目標：降低使用者啟動成本。

交付：

- setup wizard。
- Docker Compose stable profiles。
- local app command。
- dependency doctor。

測試：

- `docker compose config`。
- setup dry-run。

### P40：v1.0 Release Hardening

目標：把 beta 功能收斂成可發佈版本。

交付：

- security/legal review。
- docs 完整化。
- demo assets。
- release checklist。
- CI matrix。

測試：

- full regression。
- docs link check。
- clean clone setup smoke。

## 5. 建議執行順序

優先順序：

1. P21：先讓 P20 sidecar 被使用者看見。
2. P22–P23：再處理真實 torchcrepe 安裝與 smoke。
3. P24–P26：Demucs + stem-aware Basic Pitch。
4. P27–P31：品質、和弦、段落、指法、教學。
5. P32–P34：Web UI、job queue、合法 URL。
6. P35–P40：評估、DAW v2、cache、workspace、packaging、release。

## 6. 共通 Definition of Done

每個 P 階段完成前：

- PRD / test spec 存在。
- Red test 先失敗。
- 實作最小可行功能。
- `uv run pytest -q` 通過。
- 新 CLI 必須有 `--help` gate。
- 若涉及 artifact，必須有 `/tmp/guitar-tab-*` demo gate。
- PR/code review 完成。
- merge dev → 驗證 → merge main。
- `.omx` 不追蹤。
- commit 無 `Co-authored-by: OmX`。

## 7. 推薦下一條 Ralph 指令

```text
$ralph 使用 Ralph 完成 P21：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P21 範圍，建立 P21 PRD/test-spec，將 f0_calibration.json 整合進 viewer/interface/tutorial，讓低 pitch confidence 與 delta_semitones 可被使用者看見；保留 P20 sidecar 行為，不新增 heavy dependency；嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```
