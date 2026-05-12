# 後續開發 Roadmap：嚴格 SDD / TDD / Planning-with-files / Git Dev Flow

日期：2026-05-12  
狀態：規劃稿，可作為下一輪 `$ralph` 或 `$team` 執行輸入。  
基準分支：`main` 目前已有 MVP 骨架、繁中文檔、fixture/schema/quality gate 測試，驗證基準為 `20 passed`。

## 1. 開發原則

1. **SDD（Spec-Driven Development）先行**：任何功能先更新規格、schema、測試規格或 ADR，再寫實作。
2. **TDD 嚴格紅綠重構**：每個功能 slice 必須先有失敗測試或 golden acceptance fixture，確認紅燈後才實作。
3. **Planning with files**：所有決策、拆工、驗收、風險都落在 repo 檔案，不只存在聊天紀錄。
4. **Git dev flow**：每個開發項目使用獨立 branch、小 commit、可回滾、可驗證，禁止直接在 `main` 混雜多個主題。
5. **合法輸入與誠實輸出不放寬**：local-audio-first、URL disabled policy gate、低信心 warning、可彈 TAB hard gate 維持不變。

## 2. 目前 repo 事實基準

已存在核心檔案：

- CLI：`src/guitar_tab_generation/cli.py`
- 管線編排：`src/guitar_tab_generation/pipeline.py`
- 輸入政策：`src/guitar_tab_generation/input_adapter.py`
- 音訊前處理：`src/guitar_tab_generation/audio_preprocess.py`
- 節奏/和弦/音高/段落/編曲/渲染：`src/guitar_tab_generation/rhythm_analysis.py`、`tonal_chord_analysis.py`、`pitch_transcription.py`、`section_detector.py`、`guitar_arranger.py`、`renderer.py`
- 品質與 schema：`src/guitar_tab_generation/quality_gate.py`、`quality_reporter.py`、`schema.py`、`schemas/arrangement.schema.json`
- 測試：`tests/`，包含 input policy、schema、quality gate、fixture contract、URL stub 等。
- 文件：`README.md`、`README.zh-TW.md`、`docs/usage-guardrails.md`、`docs/usage-guardrails.zh-TW.md`
- 上游規格：`docs/plans/prd-guitar-tab-generation-mvp-20260512.md`、`docs/plans/test-spec-guitar-tab-generation-mvp-20260512.md`

## 3. SDD 檔案結構規範

後續每個 feature 建議建立：

```text
docs/plans/<feature>-prd-YYYYMMDD.md
docs/plans/<feature>-test-spec-YYYYMMDD.md
docs/adr/YYYYMMDD-<decision>.md
```

必要時新增：

```text
tests/fixtures/<feature>/
fixtures/metadata/<new_fixture>.json
fixtures/rubrics/<new_fixture>.md
docs/<feature>.zh-TW.md
```

每個 feature PRD 必須包含：

- 使用者價值與非目標。
- 輸入/輸出契約。
- `arrangement.json` 是否變更；若變更，必須同步 schema 與 migration note。
- hard fail 條件。
- 驗收指令。
- 回滾策略。

每個 feature test-spec 必須包含：

- Unit / integration / e2e 測試清單。
- 至少一個先紅燈的測試或 fixture contract。
- 對應 PRD acceptance criteria。
- 不測項目與原因。

## 4. TDD 執行規則

每個任務採用以下順序：

1. **Spec update**：更新 `docs/plans/*` 或 `docs/adr/*`。
2. **Red**：新增/修改測試，執行並確認目標測試失敗；不得跳過紅燈證據。
3. **Green**：寫最小實作讓測試通過。
4. **Refactor**：只在測試綠燈後整理，避免改變行為。
5. **Full verification**：至少跑：

```bash
PYTHONPATH=src python3 -m pytest -q
PYTHONPATH=src python3 -m guitar_tab_generation.cli --help
```

若涉及 CLI/e2e，另跑對應 fixture：

```bash
PYTHONPATH=src python3 -m guitar_tab_generation.cli transcribe fixtures/simple_chords_30_90s.wav --out /tmp/guitar-tab-simple
PYTHONPATH=src python3 -m guitar_tab_generation.cli transcribe fixtures/single_note_riff_30_90s.wav --out /tmp/guitar-tab-riff
PYTHONPATH=src python3 -m guitar_tab_generation.cli transcribe fixtures/single_note_lead_30_90s.wav --out /tmp/guitar-tab-lead
```

## 5. Git Dev Flow

### Branch 命名

- `plan/<topic>`：只改規劃/文件。
- `feature/<topic>`：新增功能。
- `test/<topic>`：補測試或 fixture。
- `fix/<topic>`：修 bug。
- `refactor/<topic>`：不改行為的整理。

### Commit 規則

所有 commit 必須遵守 AGENTS.md Lore Commit Protocol：

```text
<為什麼做這個改動，而不是只說改了什麼>

<body: 背景、限制、取捨>

Constraint: <外部限制>
Rejected: <被拒絕方案> | <原因>
Confidence: <low|medium|high>
Scope-risk: <narrow|moderate|broad>
Directive: <未來維護提醒>
Tested: <已驗證項目>
Not-tested: <未驗證項目>
```

### PR / merge gate

合併前必須滿足：

- `git status --short` 乾淨。
- 所有測試通過。
- 若 feature 變更輸出契約，schema 與繁中文檔同步更新。
- 若模型/套件行為變更，新增 fixture 或 regression test。
- 不得追蹤 `__pycache__`、`.pytest_cache`、大型輸出目錄或下載音訊。

## 6. 下一階段優先 Roadmap

### P0：建立真實 TDD 開發護欄（先做）

目標：把目前骨架轉成可安全演進的測試/規格驅動專案。

工作項目：

1. 建立 `docs/adr/` 並新增 ADR template。
2. 建立 feature PRD/test-spec template。
3. 補 `docs/development-flow.zh-TW.md`，讓未來貢獻者知道 SDD/TDD/git flow。
4. 若 CI 還不存在，新增 GitHub Actions 跑 pytest + CLI help。

驗收：

- 文件存在且連到 `README.zh-TW.md`。
- CI 或本機驗證指令明確。
- `PYTHONPATH=src python3 -m pytest -q` 通過。

### P1：把 stub 音訊分析升級為可替換 adapter 架構

目標：保留目前 fixture-driven deterministic pipeline，同時建立真實 librosa/basic-pitch 等 adapter 接口。

工作項目：

1. 在 PRD/test-spec 中定義 `AnalyzerBackend` / `TranscriberBackend` 介面。
2. 先寫測試：backend failure fallback、provenance 不得空白、低信心 warning 必出現。
3. 最小實作：fixture backend 作為 default deterministic backend；real backend 先 optional/import guarded。
4. 不新增沉重依賴到必裝路徑，除非另立 ADR。

驗收：

- fixture backend 維持 20+ 測試通過。
- real backend 缺 dependency 時有明確錯誤，不破壞 MVP 主路徑。
- `arrangement.json` provenance 可指出 backend/stage。

### P2：CLI e2e artifact contract 強化

目標：讓三個 golden fixtures 真的跑完 CLI 並驗證輸出內容，而不是只驗 schema sample。

工作項目：

1. 先寫 integration tests：三個 fixtures 跑 CLI/pipeline 到 temp out。
2. 驗證必有 `audio_normalized.wav`、`arrangement.json`、`quality_report.json`、`tab.md`、`notes.json`、`chords.json`、`sections.json`。
3. 驗證 `tab.md` warning 與 JSON report 一致。
4. 驗證平均人工 rubric baseline metadata 可被 quality gate 讀取。

驗收：

- 三個 fixture e2e 測試通過。
- URL policy gate 測試仍確認無下載副作用。

### P3：可彈性與渲染品質改善

目標：讓輸出的 TAB 更接近吉他手可讀練習稿。

工作項目：

1. 先寫 guitar_arranger tests：手位跳動、同音多位置選擇、不可彈密度降級。
2. 改善 `renderer.py`：段落化、節奏提示、inline confidence/warning。
3. 補人工 rubric 範例輸出與 snapshot-style regression。

驗收：

- 所有 position 符合 string 1–6、fret 0–20。
- `unplayable` 不會被渲染成正常 TAB。
- TAB 對三個 fixture 至少可讀、有段落、有 warning。

### P4：合法 URL future path 設計（只規劃，不立即開）

目標：為未來 YouTube/URL 願景建立合規設計，不在 MVP 中開任意下載。

工作項目：

1. ADR：合法 URL 支援條件、`--i-own-rights` 語意、allowlist、audit log。
2. Test spec：未授權 URL 必拒絕；授權 URL 若未實作仍拒絕且說明。
3. 等核心 local audio 品質足夠後再決定是否實作。

驗收：

- 沒有任何 arbitrary URL download code。
- 文件明確說明 future legal path。

### P5：Demo UI / 教學 / DAW export（延後）

目標：等 local-audio MVP 可用後再做體驗層。

候選順序：

1. Streamlit/Notebook demo：讀取現有 artifact，不改核心 pipeline。
2. 練習教學：根據 `arrangement.json` 產生段落練習建議。
3. DAW export：先研究 MusicXML/MIDI/AAF/Logic/GarageBand 可行性，再決策。

不作為近期 blocker。

## 7. 建議下一次執行切片

建議先開：`feature/dev-flow-and-ci` 或 `plan/dev-flow-and-ci`。

最小任務：

1. 補開發流程文件與 template。
2. 補 GitHub Actions pytest workflow。
3. 補 README.zh-TW 的「開發流程」入口。
4. 驗證與 commit/push。

建議執行方式：

```bash
git switch -c feature/dev-flow-and-ci
# Red: 新增一個檢查 template/docs 存在的測試或文件 lint（若採用）
PYTHONPATH=src python3 -m pytest -q
# Green: 補文件/CI
PYTHONPATH=src python3 -m pytest -q
PYTHONPATH=src python3 -m guitar_tab_generation.cli --help
git add .
git commit
git push -u origin feature/dev-flow-and-ci
```

## 8. 風險與緩解

- 風險：過早引入真實 AI 套件造成環境不穩。  
  緩解：先做 optional adapter 與 fixture backend，真實 backend 需 ADR。
- 風險：TDD 被跳過，功能先行導致回歸。  
  緩解：每個 feature test-spec 明確要求紅燈證據與驗證指令。
- 風險：YouTube 願景讓範圍失控。  
  緩解：URL gate 在 MVP 不放寬，合法 URL 另開 ADR。
- 風險：文件與實作漂移。  
  緩解：PR gate 要求改 schema/CLI/行為時同步繁中文檔與測試。
