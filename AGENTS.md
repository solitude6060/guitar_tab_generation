# AGENTS.md — Guitar Tab Generation

本檔是本 repo 的常駐代理工作契約，參考 Claude Code `CLAUDE.md` / skills 的精神，但改成適合 Codex + OMX + uv 的流程。若與系統或使用者明確指令衝突，以系統與使用者指令優先。

## 1. 回覆與文件語言

- 與使用者互動一律使用繁體中文，避免中英夾雜與未解釋縮寫。
- Commit message、程式碼、測試名稱、CLI help 可維持英文。
- 產品與開發規劃文件優先繁體中文，必要技術名詞可第一次加括號解釋。

## 2. 規格先行

- 非 trivial 任務先建立或更新 `docs/plans/` 下的 PRD / test spec / roadmap。
- 架構、法務、依賴、資料格式、輸入政策變更要補 `docs/adr/`。
- 不以現有程式碼反推需求；規格是契約，程式碼是實作。

## 3. TDD 與驗證

- 實作前先寫會失敗的測試，確認失敗理由正確，再寫最小實作。
- 常規驗證至少包含：

```bash
uv sync --group dev
uv run pytest -q
uv run guitar-tab-generation --help
```

- 新增 CLI 子命令時，也要跑該子命令 `--help`。
- 涉及 artifact 輸出時，要用 `/tmp/guitar-tab-*` 跑 fixture 手動 demo gate。

## 4. Git flow

- Feature 完成後：PR / code review → merge `dev` → 階段驗證 → merge `main`。
- 不直接在 `main` 做 feature commit。
- Commit 不得加入 `Co-authored-by: OmX`。
- `.omx/` 是本機 orchestration state，禁止追蹤與推送。
- 若目前沒有 `dev`，首次 phase merge 時建立 `dev` 並推送，再由 `dev` 合併 `main`。

## 5. Code review 與 fix log

- Feature 完成後，合併前必跑 code review。
- Review finding 先驗證再修，不盲從。
- 若 review 產生修正，新增或更新對應測試，並在 commit body 或文件中留下修正理由。

## 6. P7 之後產品方向

- P7：Practice Tutorial Generator，從 artifacts 產生練習教學。
- P8：Interface MVP，規劃好用介面，但不讓 UI 重寫 pipeline；UI 只能呼叫 CLI 或讀 artifacts。
- P9：MIDI/MusicXML export，先做通用格式，再研究 GarageBand / Logic Pro 匯入文件。

## 7. 專案 skill

Codex 實際可載入的 skill 已安裝在使用者層級：

- `~/.codex/skills/guitar-tab-product-dev/SKILL.md`

遇到本專案開發、規劃、review、merge、介面規劃時，先讀該 skill。repo 內只保留代理指南與規劃文件，不把錯誤位置的 `skills/` 目錄當成可載入 skill。
