# Test Spec：AI 自動扒吉他譜 MVP（Architect ITERATE 整合版）

## 1. 測試目標

證明 MVP 能從 **合法本機音訊** 輸入產生練歌可用、可讀、可審查的 30–90 秒吉他 sketch TAB，而不是只產生不可解釋的 raw transcription。MVP 不測任意 YouTube 下載；URL path 只驗證 disabled/stub/policy gate。

## 2. 測試素材與 Golden Fixtures

MVP 必備固定 golden fixture：

1. `simple_chords_30_90s`：合法/授權/自製簡單和弦刷奏片段。
2. `single_note_riff_30_90s`：合法/授權/自製單音 riff 片段。
3. `single_note_lead_30_90s`：合法/授權/自製單音 lead/solo 片段。

每個 fixture 必須有：
- 來源/授權記錄或自製聲明。
- 片段長度 30–90 秒；若由長音訊裁切，記錄 trim start/end。
- 人工驗收 rubric baseline 與執行紀錄。
- 期望輸出重點：主要和弦、主 riff/lead 輪廓、可接受降級與 warnings。

缺少固定 golden fixture 或人工驗收紀錄屬 hard fail。

## 3. Unit Tests

- `input_adapter`
  - 接受支援格式本機音訊；拒絕不存在/不支援檔案。
  - 預設拒絕或提示裁切超出 30–90 秒的輸入。
  - YouTube/URL path 預設不下載、不解析任意影片；觸發 disabled/stub/policy gate，訊息需提示合法替代路徑。
  - 若存在 future flag，需測 `--i-own-rights` / allowlisted source gating；未明確授權不得繼續。
- `audio_preprocess`
  - 轉出固定 sample rate/channel 的 normalized audio metadata。
  - trim start/end 正確反映在 artifact metadata。
- `rhythm_analysis`
  - 對 synthetic click/strum fixture 產出合理 tempo/beat grid。
  - `arrangement.json.timebase` 能表示 tempo、beats、bars、time signature。
- `tonal_chord_analysis`
  - 對合成 I–V–vi–IV 或簡單 open chords fixture 產出可接受 chord candidates。
  - chord confidence 低於門檻時必須生成 warning 或降級註記。
- `pitch_transcription`
  - 對單音 riff/lead fixture 產出時間與 pitch 接近的 note events。
  - note confidence 低於門檻時必須可追溯到 warning。
- `guitar_arranger`
  - note/chord events 映射到合法 string/fret 範圍（MVP：string 1–6、fret 0–20）。
  - 不產生不存在 string/fret、超出 fret 範圍、不可彈大跨度；無法映射時需降級或 hard fail。
  - 標準調弦 EADGBE 為 MVP 預設；alternate tunings 不作 MVP 必測。
- `renderer`
  - Markdown TAB 包含 metadata、sections、chords、TAB、warnings。
  - `arrangement.json` schema 穩定且可 round-trip 最小欄位。
  - inline warning 與 `quality_report.json` 警告一致。
- `quality_reporter`
  - 偵測不可彈 TAB、低信心無 warning、缺 golden/manual record 等 hard fail。
  - hard fail 時 exit code / status 明確，不得靜默產出「通過」。

## 4. `arrangement.json` Schema Tests

最小 schema 必測欄位：

- `schema_version`
- `timebase`
  - `sample_rate`
  - `tempo_bpm`
  - `beats`
  - `bars`
  - `time_signature`
- `source`
  - `input_type`
  - `input_uri`
  - `rights_attestation`
  - `trim`
  - `stems[]`，包含 stem name/path/model/confidence/provenance 資訊
- `confidence`
  - `overall`
  - `rhythm`
  - `chords`
  - `notes`
  - `fingering`
- `warnings[]`
  - `code`
  - `severity`
  - `message`
  - optional `time_range`
- `note_events[]`
  - `id`
  - `start`
  - `end`
  - `pitch_midi` 或等價 pitch 表示
  - `confidence`
  - `provenance`
- `chord_spans[]`
  - `start`
  - `end`
  - `label`
  - `confidence`
  - `provenance`
- `section_spans[]`
  - `start`
  - `end`
  - `label`
  - `confidence`
- `fretboard`
  - `supported_fret_range`: min=0, max=20
  - `tuning`
  - `capo`
- `positions[]`
  - `note_id` 或 chord reference
  - `string`
  - `fret`
  - optional `finger`
  - `confidence`
  - `playability`
- `render_hints`
  - `tab_density`
  - `show_rhythm_slashes`
  - `show_warnings_inline`
  - `preferred_output`

Schema assertions：
- 所有時間以秒為主，且可映射到 beat/bar。
- 所有 TAB note 都有合法 string/fret，或被明確標為降級/不可映射並附 warning。
- 低於預設 confidence 門檻的 note/chord/section/fingering 必須有對應 warning 或 quality report entry；MVP 預設門檻：notes 0.55、chords 0.60、sections 0.50、fingering 0.65。
- provenance 必須能指出來源 stage 與 source/stem；不可只留空白模型輸出。

### Schema / Guardrail Acceptance Mapping（Task 3 Review）

| PRD 契約 | 必要測試 | MVP 完成條件 |
|---|---|---|
| local-audio-first | CLI/input adapter 對合法本機 `mp3/wav/flac/m4a` 產生 artifact；URL fixture 只觸發 policy gate | 本機音訊 path 可跑；任意 URL path 無下載副作用 |
| URL disabled/stub/policy gate | URL without future legal gate returns explicit refusal with `URL_INPUT_DISABLED` or equivalent reason code | 不得呼叫 downloader、不得解析任意影片、不得產生假音訊 artifact |
| `arrangement.json` required schema | schema validation covers required fields in Section 4 plus provenance, thresholds, fret range | 缺 required 欄位、空 provenance、非法 string/fret 均 fail |
| low confidence warnings | notes <0.55、chords <0.60、sections <0.50、fingering <0.65 each require matching warning/report entry | 低信心無 warning/report entry 即 hard fail |
| playable TAB only | positions enforce string 1–6, fret 0–20, and `playability` in `playable/degraded/unplayable` | `unplayable` may not render as normal TAB; must fail or degrade with warning |
| golden fixture + manual rubric | all three core fixtures include rights/trim metadata and manual rubric record | missing fixture or rubric record is hard fail |
| renderer/report consistency | `tab.md` inline warnings match `arrangement.json.warnings` and `quality_report.json` | inconsistent warnings fail renderer/report tests |

### Executable Coverage Status（2026-05-12 Review）

目前 repo 仍是 greenfield planning state，尚未包含 `src/`、`tests/`、`fixtures/`、`pyproject.toml`、CLI module 或 schema validator。因此本文件中的測試仍是驗收規格，不是已存在的 executable coverage。實作完成前，Task 3 review 判定的測試債務如下：

- 建立 `arrangement.json` schema/validator 與 valid/invalid golden JSON samples。
- 建立 `input_adapter`/CLI regression：本機音訊接受、超長音訊裁切/拒絕、URL policy gate 無下載副作用。
- 建立 fixture manifest：`simple_chords_30_90s`、`single_note_riff_30_90s`、`single_note_lead_30_90s` 的權利聲明、trim metadata、人工 rubric baseline。
- 建立 quality gate tests：不可彈位置、低信心無 warning、缺 fixture/rubric、URL bypass、raw MIDI-only output 均 hard fail。
- 建立 renderer/report consistency tests：`tab.md`、`arrangement.json`、`quality_report.json` 的 warnings 與降級狀態一致。

## 5. Integration Tests

- `local audio -> analysis artifacts`
  - legal fixture audio 可產出 normalized audio、tempo、chords、notes JSON。
  - URL fixture 不會下載，會產出 policy gate/stub 結果或明確錯誤。
- `notes/chords -> playable arrangement`
  - note density 被合理簡化，輸出不是 MIDI dump。
  - 對 riff/lead fixture 至少產生一段可彈 TAB part。
- `arrangement -> tab.md`
  - 完整輸出包含段落、和弦、至少一個 TAB part、信心/警告。
  - `tab.md` 中 warnings 與 `arrangement.json` / `quality_report.json` 一致。
- optional Demucs path
  - Demucs disabled/enabled 都可跑；enabled 失敗時可 fallback 或報明確錯誤。
  - Demucs artifact/bleed 風險需進 warnings，不得被當真值。

## 6. E2E Tests

使用短合法 30–90 秒 golden 樣本：

1. 簡單和弦刷奏：驗證 tempo、段落、和弦 progression、刷法提示，可用於伴奏練習。
2. 單音 riff 片段：驗證主要 riff 可讀 TAB，string/fret 合法且可彈。
3. 單音 lead/solo 片段：驗證 lead notes 可映射成可彈 fret/string，低信心處有 warning。

Stretch / 後續 E2E（非 MVP blocker）：
- 混音片段：驗證低信心與 artifact 警告，不要求完美。
- 多樂器片段：驗證降級與誠實度。
- 完整歌曲：驗證分段與長任務處理，但不列 MVP 通過條件。
- 合法 YouTube flow：僅在已設計 `--i-own-rights` / allowlist / user-provided audio path 後才測。

每個 MVP E2E 應產生：
- `tab.md`
- `arrangement.json`
- `quality_report.json` 或等價警告摘要
- 人工驗收 rubric 記錄

## 7. 人工音樂驗收 Rubric

每首/片段 1–5 分：

- 可辨識度：能否聽/彈出原片段主要輪廓。
- 和弦可用性：和弦 progression 是否足以伴奏。
- TAB 可彈性：指法是否實際可彈、手位是否合理。
- 節奏可讀性：是否有足夠節奏/段落提示可練習。
- 誠實度：不確定或錯誤風險是否被清楚標示。

MVP 通過門檻：
- 三個核心 golden fixture 各自平均 >= 3/5，且不可有 hard fail。
- 作者可先擔任人工驗收者並留下紀錄；第二位吉他手交叉驗收是建議加分項，不是 MVP blocker。
- 不得出現大量不可彈 TAB 或無標示的高風險錯誤。

## 8. Hard Fail 條件

以下任一發生即 MVP 不通過：

1. **不可彈 TAB**：不存在 string/fret、超出支援 fret 範圍（MVP：string 1–6、fret 0–20）、明顯不可彈大跨度、或音符密度未簡化成練歌 sketch。
2. **低信心卻無 warning**：note/chord/section/fingering 低於門檻，但 `tab.md`、`arrangement.json`、`quality_report.json` 沒有對應警告或降級。
3. **缺少固定 golden fixture**：沒有 30–90 秒合法/授權/自製核心樣本。
4. **缺少人工驗收紀錄**：沒有依 rubric 留下作者或驗收者紀錄。
5. **URL policy bypass**：MVP 對任意 YouTube/URL 執行下載或解析，未經 `--i-own-rights` / allowlist / user-provided audio gate。
6. **只輸出 raw MIDI dump**：沒有段落、和弦、TAB 可讀化、信心/警告資訊。

## 9. 非目標測試

以下不作為 MVP 通過條件：

- GarageBand/Logic Pro 多軌匯入。
- 完整教學課程品質。
- 原演奏者指法一致性。
- 逐音 transcription 完美率。
- 任意 YouTube 影片下載可用性。
- 混音、多樂器、完整歌曲通用成功率。
- 第二位吉他手交叉驗收（建議但非 blocker）。

## 10. 驗證指令占位

實作後應提供：

```bash
pytest
python -m guitar_tab_generation.cli transcribe fixtures/simple_chords_30_90s.wav --out out/simple_chords
python -m guitar_tab_generation.cli transcribe fixtures/single_note_riff_30_90s.wav --out out/riff
python -m guitar_tab_generation.cli transcribe fixtures/single_note_lead_30_90s.wav --out out/lead
python -m guitar_tab_generation.cli transcribe https://www.youtube.com/watch?v=example --out out/url_stub  # 應觸發 policy gate，不下載
```

後續若支援合法 URL path，需另加明確 gating 測試：

```bash
python -m guitar_tab_generation.cli transcribe <allowlisted-url> --i-own-rights --out out/legal_url
```
