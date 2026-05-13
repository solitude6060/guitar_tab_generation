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
