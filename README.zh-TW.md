# 吉他譜生成 MVP

這是一個 **本機音訊優先（local-audio-first）** 的 AI 吉他譜生成 MVP。目標是從使用者合法提供的 30–90 秒音訊片段，產生可練歌使用的吉他 sketch TAB。

> English README: `README.md`

## MVP 範圍

本專案依據已批准的規劃文件執行：

- `docs/plans/prd-guitar-tab-generation-mvp-20260512.md`
- `docs/plans/test-spec-guitar-tab-generation-mvp-20260512.md`

第一版刻意收窄：

- **輸入**：使用者擁有、被授權使用、或自行建立的本機音訊檔。
- **長度**：30–90 秒片段，或透過 trim 產生 30–90 秒片段。
- **輸出**：`tab.md`、`arrangement.json`、`quality_report.json`。
- **吉他範圍**：標準調弦 EADGBE、string 1–6、fret 0–20。
- **非目標**：任意 YouTube 下載、alternate tuning、PDF 必備輸出、DAW 匯出、完整教學課程、完整歌曲、逐音完美或原演奏者指法保證。

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

若來源檔較長，請明確指定 30–90 秒 trim：

```bash
uv run guitar-tab-generation transcribe path/to/legal_audio.wav --trim-start 30 --trim-end 90 --out out/clip
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

MusicXML、MIDI、PDF 等可以是未來 optional output，但不是 MVP 完成條件。

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
