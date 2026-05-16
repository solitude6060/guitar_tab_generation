# 後續完整開發執行計畫（Ralph-ready）

日期：2026-05-13  
狀態：Active roadmap  
流程：uv-first + SDD + TDD + planning-with-files + git dev flow  
基準：P0 CI/hygiene 已完成；P1 backend adapter 已完成於 `feature/audio-backend-adapters`。

## 1. 全域執行規則

每一個後續項目都遵守：

1. **先規格**：更新或建立 `docs/plans/<phase>-*-prd-*.md` 與 `docs/plans/<phase>-*-test-spec-*.md`。
2. **先紅燈**：新增測試並確認目標測試失敗。
3. **再綠燈**：寫最小實作讓測試通過。
4. **再重構**：只在綠燈後整理。
5. **驗證**：至少執行：

```bash
uv sync --group dev
uv run pytest -q
uv run guitar-tab-generation --help
```

若涉及輸出 artifact，再跑：

```bash
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-simple
uv run guitar-tab-generation transcribe fixtures/single_note_riff_30_90s.wav --backend fixture --out /tmp/guitar-tab-riff
uv run guitar-tab-generation transcribe fixtures/single_note_lead_30_90s.wav --backend fixture --out /tmp/guitar-tab-lead
```

6. **Git hygiene**：
   - 不追蹤 `.omx/`。
   - 不加入 `Co-authored-by: OmX ...`。
   - 每個 phase 使用獨立 feature branch。
   - commit message 使用 Lore protocol。

## 2. Phase sequence

| Phase | Branch | 目的 | 主要驗收 |
|---|---|---|---|
| P2 CLI E2E Artifact Contract | `feature/cli-e2e-artifact-contract` | 三個 golden fixtures 透過 CLI 端到端驗證所有 artifact | CLI 產出完整 files；schema/quality/report/tab 一致 |
| P3 Playability + Renderer Quality | `feature/playability-renderer-quality` | 提升可彈性與 TAB 可讀性 | 不可彈不渲染；TAB 有段落/節奏/warning |
| P4 Legal URL Path ADR | `plan/legal-url-path-adr` | 規劃合法 URL future path，不開下載 | ADR + tests 保持 arbitrary URL blocked |
| P5 Demo / Tutorial / DAW Research | `research/demo-tutorial-daw` | 規劃 UI、教學、DAW export 研究與取捨 | research report + ADR candidates |
| P6 Artifact Viewer Demo | `feature/artifact-viewer-demo` | 讀取既有 artifacts 產生展示/練習摘要 Markdown | 三個 golden fixtures 可產生 `viewer.md` |
| P7 Practice Tutorial Generator | `feature/practice-tutorial-generator` | 從 artifacts 產生練習教學 Markdown | 三個 golden fixtures 可產生 `tutorial.md` |
| P8 Interface MVP | `feature/interface-mvp` | 產生可離線開啟的 artifact 介面，提升易用性 | 三個 golden fixtures 可產生 `interface.html` |
| P9 MIDI / MusicXML Export MVP | `feature/midi-musicxml-export` | 產生 MusicXML / MIDI 通用匯出 | 三個 golden fixtures 可產生 `.musicxml` 與 `.mid` |
| P10 Local 4090 AI Runtime + MiniMax Backup | `feature/local-ai-runtime-resources` | 本機 4090 AI runtime 檢查與 MiniMax 備援政策 | `doctor-ai` / `ai-resources` 可用 |
| P11 Full Song Length Support | `feature/full-song-length-support` | 支援合法本機 3–8 分鐘完整歌曲輸入 | 180s/480s accepted；artifact 有 full-song chunk plan |
| P12 FFmpeg Local Audio Ingest | `feature/ffmpeg-local-audio-ingest` | 支援非 WAV 本機音訊自動長度偵測與 normalized WAV 轉檔 | mp3/flac/m4a use ffprobe + ffmpeg locally |
| P13 Local AI Backend Registry | `feature/local-ai-backend-registry` | 建立本機 AI backend/model route 可檢查狀態 | `ai-backends` CLI lists Basic Pitch/Demucs/torchcrepe/Essentia/local LLM |
| P14 Docker Compose Local AI Runtime | `feature/docker-compose-ai-runtime` | 建立 dev/gpu-ai/llm/cloud-backup compose profiles | `docker compose config`; dev image supports uv/ffmpeg CLI |
| P15 Model Download Smoke Harness | `feature/model-download-smoke-harness` | 安全、可重現的本機模型下載/整合 smoke harness | 預設不下載/不使用 GPU；opt-in + VRAM guard |
| P16 DAW Multi-track Export Bundle | `feature/daw-multitrack-export` | 產生 GarageBand / Logic 可直接匯入的多軌 bundle | `export --format daw` + `daw_bundle` 檢核 |
| P17 DAW Workflow Usability | `feature/daw-workflow-usability` | 將 DAW 匯出導入更好用介面與教學動線（含 `interface`） | 介面顯示 DAW 匯出策略與檔案導引 |
| P18 Basic Pitch Local Backend MVP | `feature/basic-pitch-backend` | 接入第一個真實本機 AI note backend | `transcribe --backend basic-pitch` 產生非 fixture notes artifact |

## 3. Recommended Ralph commands

### P2

```text
使用 Ralph 完成 P2：依照 docs/plans/p2-cli-e2e-artifact-contract-prd-20260513.md 和 docs/plans/p2-cli-e2e-artifact-contract-test-spec-20260513.md，嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```

### P3

```text
使用 Ralph 完成 P3：依照 docs/plans/p3-playability-renderer-quality-prd-20260513.md 和 docs/plans/p3-playability-renderer-quality-test-spec-20260513.md，嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```

### P4

```text
使用 Ralph 完成 P4 規劃：建立合法 URL path ADR 與防回歸測試，維持 arbitrary URL disabled；嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```

### P5

```text
使用 Ralph 完成 P5 research planning：規劃 demo、教學生成、MIDI/MusicXML/DAW export 的研究與驗收路徑；不實作大型功能；非必要不要找使用者。
```

## 4. Stop condition

整體 roadmap 不要求一次完成所有 phase；每個 phase 必須在：

- 本機 uv 驗證通過。
- CI/hygiene 通過。
- phase 文件更新。
- commit + push 完成。
- Ralph completion audit 有 JSON evidence。

後才可宣告該 phase 完成。


### P6

```text
使用 Ralph 完成 P6：依照 docs/plans/p6-artifact-viewer-demo-prd-20260513.md 和 docs/plans/p6-artifact-viewer-demo-test-spec-20260513.md，新增零重依賴 CLI artifact viewer；嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```


### P7

```text
使用 Ralph 完成 P7：依照 docs/plans/p7-practice-tutorial-generator-prd-20260513.md 和 docs/plans/p7-practice-tutorial-generator-test-spec-20260513.md，新增零重依賴 CLI practice tutorial generator；嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```


### P8

```text
使用 Ralph 完成 P8：依照 docs/plans/p8-interface-mvp-plan-20260513.md，新增 artifact-first interface；UI 不重寫 pipeline、不下載 URL；嚴格 SDD/TDD/git flow，用 uv。
```


### P11

```text
使用 Ralph 完成 P11：依照 docs/plans/p11-full-song-length-support-prd-20260514.md 與 docs/plans/p11-full-song-length-support-test-spec-20260514.md，支援合法本機 3–8 分鐘完整歌曲輸入；保留 30–90 秒 fixture clip；artifact 需包含 duration_class 與 processing_plan；嚴格 SDD/TDD/git flow，用 uv。
```


### P12

```text
使用 Ralph 完成 P12：依照 docs/plans/p12-ffmpeg-local-audio-ingest-prd-20260515.md 與 docs/plans/p12-ffmpeg-local-audio-ingest-test-spec-20260515.md，新增本機 ffprobe/ffmpeg ingest；非 WAV 本機音訊可自動取得長度並轉為 audio_normalized.wav；嚴格 SDD/TDD/git flow，用 uv。
```


### P13

```text
使用 Ralph 完成 P13：依照 docs/plans/p13-local-ai-backend-registry-prd-20260515.md 與 docs/plans/p13-local-ai-backend-registry-test-spec-20260515.md，新增本機 AI backend registry 與 `ai-backends` CLI；只偵測 Basic Pitch、Demucs、torchcrepe、Essentia/local feature、local LLM 狀態，不安裝重依賴、不跑模型推論；嚴格 SDD/TDD/git flow，用 uv。
```


### P14

```text
使用 Ralph 完成 P14：依照 docs/plans/p14-docker-compose-ai-runtime-prd-20260515.md 與 docs/plans/p14-docker-compose-ai-runtime-test-spec-20260515.md，新增 Docker Compose dev/gpu-ai/llm/cloud-backup profiles；dev 支援 uv/pytest/CLI/ffmpeg，gpu-ai 預留 CUDA/PyTorch，MiniMax token 只用環境變數；嚴格 SDD/TDD/git flow，用 uv。
```


### P15

```text
使用 Ralph 完成 P15：依照 docs/plans/p15-model-download-smoke-harness-prd-20260515.md 與 docs/plans/p15-model-download-smoke-harness-test-spec-20260515.md，新增 safe model-smoke CLI；預設不下載、不使用 GPU，只有 --download / MODEL_SMOKE_DOWNLOAD=1 與 --allow-gpu / GPU_TESTS_ENABLED=1 才執行；必須檢查 GPU free VRAM，VRAM 不足時 skip；嚴格 SDD/TDD/git flow，用 uv。
```

### P16

```text
使用 Ralph 完成 P16：依照 docs/plans/p16-daw-multitrack-export-prd-20260516.md 與 docs/plans/p16-daw-multitrack-export-test-spec-20260516.md，實作 `export --format daw`，讓 chunked_full_song 轉譯可直接匯入 GarageBand / Logic 的可管理多軌 bundle；保留既有 musicxml/midi 行為；嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```

### P17

```text
使用 Ralph 完成 P17：依照 docs/plans/p17-daw-workflow-usability-prd-20260516.md 與 docs/plans/p17-daw-workflow-usability-test-spec-20260516.md，完成 DAW 匯出可用性強化（interface 顯示 DAW 匯入策略與可匯入檔、操作步驟文字）並補上對應單元/E2E 測試；嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```

### P18

```text
使用 Ralph 完成 P18：依照 docs/plans/p18-basic-pitch-local-backend-prd-20260516.md 與 docs/plans/p18-basic-pitch-local-backend-test-spec-20260516.md，下載並接入 Basic Pitch 作為第一個真實本機 AI note backend，讓 `transcribe --backend basic-pitch` 可用；保留 fixture 為 deterministic default，嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```
