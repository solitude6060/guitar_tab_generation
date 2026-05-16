# 吉他譜生成 MVP

這是一個 **本機音訊優先（local-audio-first）** 的 AI 吉他譜生成 MVP。目標是從使用者合法提供的 30–90 秒音訊片段，以及必備支援的 3–8 分鐘完整歌曲，產生可練歌使用的吉他 sketch TAB。

> English README: `README.md`

## MVP 範圍

本專案依據已批准的規劃文件執行：

- `docs/plans/prd-guitar-tab-generation-mvp-20260512.md`
- `docs/plans/test-spec-guitar-tab-generation-mvp-20260512.md`

第一版刻意收窄：

- **輸入**：使用者擁有、被授權使用、或自行建立的本機音訊檔。
- **格式**：`.wav`、`.mp3`、`.flac`、`.m4a`；非 WAV 需要本機 `ffprobe` 與 `ffmpeg`。
- **長度**：30–90 秒片段保留給 golden fixtures；正式完整歌曲必備支援 3–8 分鐘（180–480 秒）。
- **輸出**：`tab.md`、`arrangement.json`、`quality_report.json`。
- **吉他範圍**：標準調弦 EADGBE、string 1–6、fret 0–20。
- **非目標**：任意 YouTube 下載、alternate tuning、PDF 必備輸出、專有 DAW session 直接輸出、完整教學課程、逐音完美或原演奏者指法保證。
- **可選 DAW 匯出**：`--format daw` 可輸出可直接提供 GarageBand / Logic 匯入的多軌目錄（依 full-song chunk 計畫分軌）。
- **可選 AI Backend**：同步 `ai` dependency group 後，可使用 `--backend basic-pitch` 啟用第一個真實本機 note transcription backend。

## 輸入政策 guardrail

MVP **不得下載或解析任意 URL**。YouTube/URL 輸入在第一版只是一個 disabled policy gate / stub，直到未來設計合法流程。

URL 預期行為：

1. 在任何媒體處理前偵測 `http://` / `https://`。
2. 回傳明確拒絕，例如 `URL_INPUT_DISABLED` 或 `URL_POLICY_GATE_DISABLED`。
3. 告知使用者改提供合法本機音訊檔。
4. 不建立下載音訊、暫存媒體檔、或 URL 衍生轉錄 artifact。


## 開發環境（uv）

本專案使用 `uv` 管理 Python 開發環境。

```bash
uv sync --group dev
uv run pytest -q
uv run guitar-tab-generation --help
```

若要跑 golden fixture：

```bash
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --out /tmp/guitar-tab-simple
```

## CLI 使用方式

建議透過 uv 執行 console script：

```bash
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out out/simple_chords
```

若來源檔較長，請明確指定 trim；有效長度需是 30–90 秒片段或 3–8 分鐘完整歌曲：

```bash
uv run guitar-tab-generation transcribe path/to/legal_audio.wav --trim-start 30 --trim-end 90 --out out/clip
uv run guitar-tab-generation transcribe path/to/legal_audio.wav --trim-start 0 --trim-end 240 --out out/full_song
```

對 `.mp3`、`.flac`、`.m4a`，CLI 會用本機 `ffprobe` 讀取長度，並用本機 `ffmpeg` 產生 `audio_normalized.wav`：

```bash
uv run guitar-tab-generation transcribe path/to/legal_song.mp3 --out out/legal_song
```

安裝重模型前，可先檢查目前選定的本機 AI backend 路線：

```bash
uv run guitar-tab-generation ai-backends
uv run guitar-tab-generation ai-backends --json
```

URL 只應用於測試 policy gate：

```bash
uv run guitar-tab-generation transcribe 'https://www.youtube.com/watch?v=example' --out out/url_stub
# 預期：被 URL policy gate 阻擋；不下載、不解析媒體。
```

## 成功輸出目錄

成功的本機音訊流程應產生：

```text
out/<clip>/
├── audio_normalized.wav
├── arrangement.json
├── quality_report.json
└── tab.md
```

MusicXML、MIDI、DAW bundle 等可為可選輸出；不是 MVP 必要條件，但 `--format daw` 已可用，並可搭配 `interface.html` 查看導入步驟。

DAW 匯出使用說明請見：

- `docs/daw-bundle-export.md`
- `docs/daw-bundle-export.zh-TW.md`

Basic Pitch backend 使用說明請見：

- `docs/basic-pitch-backend.md`
- `docs/basic-pitch-backend.zh-TW.md`

Torch-first 後續 AI backend 路線與 smoke gate 請見：

- `docs/torch-first-ai-backend-roadmap.md`
- `docs/torch-first-ai-backend-roadmap.zh-TW.md`

## 驗證

從 repo root 執行：

```bash
uv run pytest -q
uv run guitar-tab-generation --help
```

目前驗證基準：

- `20 passed`
- CLI help 可執行

後續開發規劃請看：

- `docs/plans/backlog-20260512.md`
- `docs/development-flow.zh-TW.md`

完整使用與驗收規則請看：

- `docs/usage-guardrails.zh-TW.md`
- `docs/usage-guardrails.md`
