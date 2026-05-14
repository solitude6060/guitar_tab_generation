# 使用規範與驗收 Guardrails

## 本機音訊是 MVP 唯一成功路徑

只有在輸入是具備明確權利聲明的本機音訊檔時，才屬於 MVP 範圍：

- 自行建立的音訊；
- 已授權 / 已取得 license 的音訊；
- 公領域音訊，且有來源記錄。

MVP 支援副檔名：`.wav`、`.mp3`、`.flac`、`.m4a`。接受的有效長度為：

- 30–90 秒：deterministic 練習片段與 golden fixtures。
- 3–8 分鐘（180–480 秒）：必備支援的完整歌曲。

90–180 秒之間的中間長度會先被拒絕，直到後續產品模式定義清楚 UX。更長的來源檔必須明確 trim 到上述其中一個支援區間。

非 WAV 本機音訊需要本機 `ffprobe` 取得長度，並用本機 `ffmpeg` 轉成 `audio_normalized.wav`。若工具缺失，專案必須回報可行動的本機工具錯誤；不得改用下載、上傳或雲端媒體解析。

## URL / YouTube policy gate

URL 支援是未來合法流程，不是 MVP 功能。MVP 行為是 stub / policy gate：

| 輸入 | 預期行為 |
|---|---|
| 未來合法 gate 之前的 `https://...` | 在下載或解析前阻擋 |
| YouTube URL | 在下載或解析前阻擋 |
| allowlist URL | MVP 不實作，留到 post-MVP ADR |
| 本機檔案路徑 | 繼續本機音訊驗證 |

policy response 應包含穩定 reason code，例如 `URL_INPUT_DISABLED` 或 `URL_POLICY_GATE_DISABLED`，並告知下一步：提供合法本機音訊片段，或合法本機 3–8 分鐘完整歌曲。

## 輸出 artifact 契約

每次成功的本機音訊流程都必須產生：

- `arrangement.json`：共享機器可讀契約，包含 timebase、source provenance、confidence、warnings、note/chord/section spans、fretboard、positions、render hints。
- `tab.md`：人類可讀 sketch TAB，包含 metadata、sections、chords、warnings，以及 fixture 需要時至少一個 playable TAB part。
- `quality_report.json`：quality gate 摘要、warnings、hard failures、degraded status。

## Hard-fail 與降級規則

遇到以下情況必須 fail 或明確降級：

1. TAB position 的 string/fret 非法（`string` 不在 1–6，或 `fret` 不在 0–20）。
2. 低信心 note/chord/section/fingering 沒有對應 warning 或 quality-report entry。
3. 缺少 golden fixture metadata 或人工 rubric record。
4. URL policy gate 被繞過，或任意 URL input 觸發 downloader/parser。
5. 輸出只有 raw MIDI/note data，沒有 readable sections、chords、TAB、warnings。
6. `positions[].playability` 是 `unplayable`，卻被當成正常 TAB 渲染。

允許的 `positions[].playability`：

- `playable`：可渲染成正常 TAB。
- `degraded`：只能搭配 warning 或 chord-only / 文字 fallback。
- `unplayable`：必須 hard fail，除非從正常 TAB 輸出移除並清楚回報。

## Golden fixture 驗收流程

Phase 0 必須建立三個合法 fixture，才能宣稱 e2e MVP 通過：

1. `simple_chords_30_90s`
2. `single_note_riff_30_90s`
3. `single_note_lead_30_90s`

每個 fixture 需要：

- 權利 / 來源聲明；
- trim start/end 或 duration metadata；
- expected musical focus；
- manual rubric baseline；
- 由目前版本生成的 `tab.md`、`arrangement.json`、`quality_report.json`。

人工 rubric 以 1–5 分評估：可辨識度、和弦可用性、TAB 可彈性、節奏可讀性、誠實度。MVP 通過門檻是每個核心 fixture 平均 >= 3/5 且沒有 hard failure。

## Contributor checklist

完成任何變更前請確認：

- [ ] 保留 local-audio-first 規則。
- [ ] URL 行為仍是 no-download policy gate。
- [ ] `arrangement.json` 欄位與 PRD / test-spec required schema 向後相容。
- [ ] 低信心值會產生 warnings。
- [ ] 不可彈 TAB 不會被輸出成正常 TAB。
- [ ] `tab.md`、`arrangement.json`、`quality_report.json` 的 warnings 一致。
- [ ] `uv run pytest -q` 通過，或清楚記錄任何測試限制。
