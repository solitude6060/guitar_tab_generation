# Guitar Tab Agent Guide

本文件是給本專案代理使用的精簡操作指南，對應根目錄 `AGENTS.md` 與已安裝的 Codex skill：

- `~/.codex/skills/guitar-tab-product-dev/SKILL.md`

## Mission

把「輸入合法音訊 → 產生吉他譜 / 練習資料 / 未來匯出」做成可驗證、可練習、可逐步擴充的 AI 產品。

## Non-negotiables

- 繁體中文回覆使用者。
- 給使用者看的文件必須有繁中版本。
- 規格、測試、實作、驗證、code review、merge flow 缺一不可。
- 不開任意 URL / YouTube 下載。
- 不隱藏低信心結果；warning 必須保留到 viewer / tutorial / export。
- `.omx/` 不追蹤；commit 無 OmX co-author。

## Current product ladder

1. P6 Artifact Viewer：artifact 可讀。
2. P7 Practice Tutorial：artifact 可練。
3. P8 Interface MVP：產品變好用，但 UI 讀 artifacts，不重寫 pipeline。
4. P9 MIDI/MusicXML：先通用匯出，再研究 GarageBand / Logic Pro。

## Before every merge

```bash
uv sync --group dev
uv run pytest -q
uv run guitar-tab-generation --help
```

Feature branch 必須先 code review，再進 `dev`，驗證後再進 `main`。
