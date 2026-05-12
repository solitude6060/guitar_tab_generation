# 開發流程：嚴格 SDD / TDD / Planning with files / Git Dev Flow

本專案所有後續功能都必須遵守「先規格、再測試、後實作」的流程。

## 1. SDD：Spec-Driven Development

功能開始前，先寫或更新：

- `docs/plans/<feature>-prd-YYYYMMDD.md`
- `docs/plans/<feature>-test-spec-YYYYMMDD.md`
- `docs/adr/YYYYMMDD-<decision>.md`（若涉及架構/依賴/schema/政策）

沒有檔案化規格，不開始寫功能。

## 2. TDD：Red / Green / Refactor

每個功能 slice 必須：

1. 先新增會失敗的測試或 fixture contract。
2. 執行測試確認紅燈。
3. 寫最小實作讓測試綠燈。
4. 綠燈後才重構。
5. 最後跑完整驗證。

基本驗證：

```bash
PYTHONPATH=src python3 -m pytest -q
PYTHONPATH=src python3 -m guitar_tab_generation.cli --help
```

涉及輸出 artifact 時，至少跑一個 golden fixture：

```bash
PYTHONPATH=src python3 -m guitar_tab_generation.cli transcribe fixtures/simple_chords_30_90s.wav --out /tmp/guitar-tab-simple
```

## 3. Planning with files

聊天中的計畫不算完成。重要資訊必須落到 repo：

- Roadmap / feature plan：`docs/plans/`
- ADR：`docs/adr/`
- 使用者文件：`docs/*.zh-TW.md`
- 測試 fixture 與 rubric：`fixtures/`、`tests/fixtures/`

## 4. Git Dev Flow

### Branch

- `plan/<topic>`：規劃與文件。
- `feature/<topic>`：功能。
- `test/<topic>`：測試/fixture。
- `fix/<topic>`：修 bug。
- `refactor/<topic>`：不改行為整理。

### Commit

Commit message 必須遵守 Lore protocol，第一行寫「為什麼」，不是只寫「改了什麼」。建議至少包含：

```text
Confidence: high|medium|low
Scope-risk: narrow|moderate|broad
Tested: <已跑驗證>
Not-tested: <未跑項目>
```

### Merge gate

合併前必須：

- 測試通過。
- CLI help 可執行。
- 文件與 schema 同步。
- `git status --short` 乾淨。
- 不提交 cache、暫存輸出、下載媒體或大型 artifact。

## 5. MVP 不可放寬的 guardrails

- MVP 只支援合法本機音訊。
- 任意 URL / YouTube 必須走 disabled policy gate，不下載、不解析。
- 低信心必須有 warning。
- 不可彈 TAB 不得被渲染成正常 TAB。
- `arrangement.json` schema 是共享契約，不能任意破壞。
