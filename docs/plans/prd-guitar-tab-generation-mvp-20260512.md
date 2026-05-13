# PRD / RALPLAN-DR：AI 自動扒吉他譜 MVP（Architect ITERATE 整合版）

## 0. 來源與範圍

- 需求來源：`.omx/specs/deep-interview-guitar-tab-generation-product.md`
- Repo 狀態：greenfield；目前僅有 `.omx` 狀態、訪談、規格檔。
- MVP 目標：以 **local-audio-first** 的本機流程，輸入使用者已合法取得/授權/自製的 30–90 秒音訊片段，輸出人類可讀、練歌可用的 sketch TAB。
- MVP 音樂範圍：先通過 **簡單和弦刷奏** 與 **單音 riff/lead** 的短片段；輸出以「可練習的近似編曲」為目標，不承諾完整歌曲、混音、多樂器或原演奏者精準指法。
- YouTube 願景：YouTube URL 是後續合法路徑；MVP 預設 **disabled/stub/policy gate**，不內建任意下載流程。若日後支援，必須符合 `--i-own-rights`、allowlisted source，或要求使用者自行提供音訊。
- MVP 包含：和弦、段落、節奏/刷法提示、單音 riff/lead sketch、AI 推測可彈指法、不確定性標示、`arrangement.json` 中間格式。
- MVP 延後：GarageBand/Logic Pro 多軌匯入、完整教學、原演奏者精準指法、逐音完美、完整歌曲、混音/多樂器通用處理、任意 YouTube 下載。
- 成本邊界：優先本機/開源工具；不自動假設付費雲端或大量 GPU 成本。

## 1. RALPLAN-DR Summary

### Principles

1. **練歌可用優先於逐音完美**：輸出需讓吉他手可練、可辨識歌曲結構與主要彈奏內容。
2. **透明標示不確定性**：模型推測、分離 artifact、低信心和弦/音符都需在輸出中標明；低信心無 warning 屬 hard fail。
3. **local-audio-first 與合法輸入**：MVP 主路徑是使用者提供合法音訊；YouTube URL 預設 disabled/stub/policy gate，不做任意下載器。
4. **可替換管線**：音源分離、轉錄、和弦辨識、指法生成、渲染輸出需模組化，允許日後替換模型。
5. **人類可讀輸出先行**：文字 TAB/Markdown 是 MVP 必備；MusicXML/PDF/MIDI 作為輔助或後續輸出。

### Top 3 Decision Drivers

1. **輸出是否能被吉他手拿來練 30–90 秒片段**：段落、和弦、主 riff/lead、指法與節奏提示比 raw note accuracy 更重要。
2. **管線可驗證與可迭代**：每個階段需有中間 artifact，尤其 `arrangement.json`，方便人工聽辨、除錯、替換模型。
3. **合法性、成本與部署摩擦低**：預設本機 CLI/簡易 demo，避免依賴付費雲端與不合規下載流程。

### Viable Options

#### Option A：本機批次 CLI 管線（建議 MVP 主線）

**概念**：以 CLI 接收本機合法音訊檔，跑本機分析管線，輸出 Markdown/TAB、`arrangement.json`、品質報告與可選 MusicXML/PDF。

**Pros**
- 最快建立可驗證 MVP；greenfield 低風險。
- 成本可控，預設使用開源工具。
- 易保留中間 artifact，利於人工音樂驗收與模型替換。
- 避開前端/上傳/帳號/雲端成本等非核心問題。
- 以 local-audio-first 明確降低版權/政策風險。

**Cons**
- 非一般使用者最友善。
- 長音訊處理時間與本機依賴安裝可能影響體驗。
- YouTube URL 只能先做 stub/policy gate，不能滿足「貼 URL 立即扒譜」的終局體驗。

#### Option B：Notebook / Streamlit 本機互動 demo

**概念**：用簡易 UI 上傳音訊，顯示段落、和弦、TAB 與中間信心資訊；YouTube URL 仍維持 disabled/stub/policy gate。

**Pros**
- 較適合 demo 與人工聽辨回饋。
- 可逐段播放/檢視，有助改善 TAB 可用性。
- 對非工程使用者比 CLI 友善。

**Cons**
- UI 會增加 MVP 實作面與維護面。
- 若核心轉錄品質尚未穩定，UI 投資可能過早。
- 檔案處理、暫存與長任務狀態會引入額外設計。

#### Option C：雲端 API / SaaS 風格 MVP（淘汰於初版）

**淘汰理由**
- 需求明確限制「不自動假設付費雲端/大量成本」。
- 會引入帳號、儲存、版權處理、佇列、GPU/CPU 成本與資安範圍。
- 對驗證核心技術假設不是必要條件。

## 2. 初版決策 / ADR

### Decision

採用 **Option A：本機批次 CLI 管線，local-audio-first** 作為 MVP 主線；YouTube URL 在 MVP 僅提供 disabled/stub/policy gate，不內建任意下載流程。核心管線穩定後可包一層 Notebook/Streamlit demo。

### Drivers

- 最短路徑驗證「合法本機音訊 → 練歌可用 sketch TAB」核心價值。
- 保留完整中間 artifact，方便 Architect/Critic 與音樂人工驗收。
- 符合低成本、合法輸入、greenfield 小步交付的限制。
- 明確避免 MVP 被實作成任意影片下載工具。

### Alternatives Considered

- Notebook/Streamlit：保留為展示層，不作為初始核心交付。
- 雲端/SaaS：因成本、法務與非核心複雜度，初版淘汰。
- 任意 YouTube URL 下載：因版權/平台政策風險，MVP 淘汰；合法 URL 支援保留為後續 gated path。

### Consequences

- 初版使用門檻偏工程化，但能快速驗證音樂可用性。
- 架構需從一開始保留清楚資料模型，避免 CLI 原型變成不可替換腳本。
- 後續若轉為 UI，只需呼叫穩定管線與讀取 artifact。
- 對使用者願景的 YouTube flow 需誠實標成 future legal path，而非 MVP 承諾。

### Follow-ups

- Architect 審查：模組邊界、資料模型、轉錄品質瓶頸、合法 URL 策略。
- Critic 審查：驗收標準是否可測、人工音樂驗收是否足夠客觀、風險是否明確。

## 3. MVP 階段計畫

### Phase 0：專案骨架與合法 golden 樣本集

- 建立 Python 專案骨架、CLI 入口、設定檔、輸出目錄規範。
- 建立固定 golden fixture 集：30–90 秒合法/授權/自製片段，至少包含簡單和弦刷奏、單音 riff、單音 lead。
- 每個 golden fixture 需有人工驗收紀錄/rubric baseline；缺少固定 golden fixture 或人工驗收紀錄屬 MVP hard fail。
- 定義統一 artifact 結構：`audio_normalized.wav`、可選 `stems/`、`notes.json`、`chords.json`、`sections.json`、`arrangement.json`、`tab.md`、`quality_report.json`。

### Phase 1：輸入與音訊前處理

- 支援 local `mp3/wav/flac/m4a` 等音訊檔。
- CLI 預設要求 30–90 秒片段；超過範圍需明確裁切參數或拒絕並提示。
- YouTube URL path 預設 disabled/stub/policy gate：不下載、不解析任意影片；只輸出明確說明與合法替代路徑。
- 若後續開啟 URL 支援，必須要求 `--i-own-rights` 或 allowlisted source，且仍可要求使用者自行提供音訊。
- 使用 ffmpeg/ffprobe 做轉檔、取樣率正規化、片段裁切。

### Phase 2：音訊分析基線

- 使用 librosa 做 tempo/beat/onset 基礎分析。
- 使用 Essentia 或等價 tonal 分析抽取 key/chord descriptors，建立和弦候選與信心。
- 可選 Demucs 做 source separation；MVP 不依賴分離成功。混音、多樂器與完整歌曲列 stretch/後續，若處理需標記低信心與 artifact 風險。

### Phase 3：音高 / note event 轉錄

- 使用 Spotify Basic Pitch 或等價工具作音訊到 MIDI/note events 的初版轉錄。
- 核心通過樣本先限單音 riff/lead；polyphonic/mixed guitar 不作 MVP 必過。
- 針對吉他可彈範圍、音符密度、持續時間做後處理。
- 保留模型信心與來源 stem/provenance，避免把低信心內容誤呈現為確定答案。

### Phase 4：吉他編曲與指法推測

- 建立 guitar fretboard model：標準調弦 EADGBE 為 MVP 預設；支援 fret 範圍固定為 **0–20 fret**，超出範圍必須降級/警告或 hard fail。
- 將 note events / chord candidates 映射成可彈 string/fret positions、chord shapes、riff/lead phrase。
- 用 heuristic 或輕量搜尋最佳化：手位移動少、常見 chord shape 優先、避免不可彈跨度。
- 明確標示「推測指法」，不宣稱為原演奏者指法。
- 不可彈 TAB 屬 hard fail：若無法產生可彈映射，應降級為 chord-only/警告或失敗，而不是輸出假 TAB。

### Phase 5：結構化輸出與渲染

- 必備輸出：Markdown/TXT TAB，包含段落、和弦、節奏提示、riff/lead TAB、不確定性註記。
- 必備機器可讀輸出：`arrangement.json`，供除錯、測試與未來 UI 使用。
- 可選輸出：MusicXML/MIDI；用 music21 建模、MuseScore CLI 批次轉 PDF/MusicXML/MIDI（若本機可用）。

### Phase 6：MVP 驗收與迭代

- 使用固定合法 golden 樣本跑端到端流程。
- 由作者依 golden fixture rubric 先做人工驗收；第二位吉他手交叉驗收是建議加分項，不是 MVP blocker。
- 將失敗案例分類：分離失敗、和弦錯誤、note density 過高、節奏量化錯誤、指法不可彈、低信心未標示。

## 4. 初版架構

### 核心模組

1. `input_adapter`：處理 local audio 與 URL disabled/stub/policy gate。
2. `audio_preprocess`：ffmpeg/ffprobe normalize、trim、metadata。
3. `source_separation`：Demucs wrapper，可開關；輸出 stems 與 artifact 註記；非 MVP hard dependency。
4. `rhythm_analysis`：librosa tempo/beat/onset。
5. `tonal_chord_analysis`：Essentia/key/chord candidates。
6. `pitch_transcription`：Basic Pitch note/MIDI event extraction。
7. `guitar_arranger`：音符/和弦到 fret/string/fingering 的 playable mapping。
8. `section_detector`：初版可用 onset/energy/chord repetition heuristic；必要時先人工/簡化段落。
9. `renderer`：Markdown TAB、JSON、可選 MusicXML/PDF/MIDI。
10. `quality_reporter`：信心、警告、失敗原因、不確定性摘要；負責 hard fail 條件。

### 資料流

`Local legal audio`
→ `normalized audio`
→ optional `stems`
→ `tempo/beat grid`
→ `chord/key candidates`
→ `note events`
→ `section + phrase grouping`
→ `guitar playable arrangement`
→ `TAB/Markdown + arrangement.json + quality_report.json + optional MusicXML/PDF/MIDI`

URL 輸入在 MVP：`URL` → `policy gate/stub` → `拒絕任意下載並提示合法替代路徑`。

## 5. 輸出格式策略

- **MVP 必備**：`tab.md` 或 `tab.txt`
  - song metadata、tempo/key、段落、和弦 progression、riff/lead TAB、刷法/節奏提示、信心與限制。
- **MVP 必備**：`arrangement.json`
  - 結構化 timebase、provenance、confidence、warnings、notes/chords/sections、fret/string positions、render hints，利於測試與未來 UI。
- **MVP 必備**：`quality_report.json` 或等價品質摘要
  - 彙總低信心、不可彈/降級、缺漏欄位、artifact 風險與 hard fail 結果。
- **可選**：`output.musicxml` / `output.pdf` / `output.mid`
  - 用於分享或列印，不作 MVP 完成必要條件。
- **延後**：GarageBand/Logic Pro 多軌 session、完整教學內容、Guitar Pro 專有格式。

### `arrangement.json` 最小 schema（MVP）

```json
{
  "schema_version": "0.1.0",
  "timebase": {
    "sample_rate": 44100,
    "tempo_bpm": 96.0,
    "beats": [{"time": 0.0, "beat": 1}],
    "bars": [{"index": 1, "start": 0.0, "end": 2.5}],
    "time_signature": "4/4"
  },
  "source": {
    "input_type": "local_audio",
    "input_uri": "fixtures/simple_chords.wav",
    "rights_attestation": "user_provided",
    "trim": {"start": 0.0, "end": 60.0},
    "stems": [{"name": "mix", "path": "audio_normalized.wav", "model": null, "confidence": 1.0, "provenance": {"stage": "audio_preprocess", "input": "local_audio"}}]
  },
  "confidence": {
    "overall": 0.72,
    "rhythm": 0.8,
    "chords": 0.7,
    "notes": 0.65,
    "fingering": 0.75,
    "thresholds": {"notes": 0.55, "chords": 0.60, "sections": 0.50, "fingering": 0.65}
  },
  "warnings": [
    {"code": "LOW_NOTE_CONFIDENCE", "severity": "warning", "message": "Lead line is approximate", "time_range": [12.0, 18.5]}
  ],
  "note_events": [
    {
      "id": "n1",
      "start": 1.25,
      "end": 1.55,
      "pitch_midi": 64,
      "pitch_name": "E4",
      "velocity": 0.7,
      "confidence": 0.82,
      "provenance": {"stage": "pitch_transcription", "stem": "mix", "model": "basic_pitch"}
    }
  ],
  "chord_spans": [
    {"start": 0.0, "end": 2.5, "label": "G", "confidence": 0.78, "provenance": {"stage": "tonal_chord_analysis", "stem": "mix"}}
  ],
  "section_spans": [
    {"start": 0.0, "end": 16.0, "label": "Verse/Riff A", "confidence": 0.66}
  ],
  "fretboard": {
    "tuning": ["E2", "A2", "D3", "G3", "B3", "E4"],
    "capo": 0,
    "supported_fret_range": {"min": 0, "max": 20}
  },
  "positions": [
    {"note_id": "n1", "string": 1, "fret": 0, "finger": null, "confidence": 0.8, "playability": "playable"}
  ],
  "render_hints": {
    "tab_density": "sketch",
    "show_rhythm_slashes": true,
    "show_warnings_inline": true,
    "preferred_output": "markdown"
  }
}
```

最小要求：所有時間以秒為主並可映射 beat/bar；所有低於預設門檻（notes 0.55、chords 0.60、sections 0.50、fingering 0.65）的事件必須可追溯到 `confidence` 與 `warnings`；所有 TAB 音符必須有合法 `string`/`fret`（string 1–6、fret 0–20）或明確降級/警告。

### MVP 行為契約 / Review Gate（2026-05-12）

本節將 Task 3 review 的 guardrails 固化成實作者不可放寬的共享契約；若與早期 deep-interview 願景衝突，以本 PRD 與 Test Spec 為準。

- **輸入策略**：MVP 主路徑只接受本機合法音訊。`http://`、`https://`、YouTube 或其他 URL 在 MVP 必須走 disabled/stub/policy gate；不得下載、不得解析媒體、不得建立暫存音訊。
- **URL gate 回應契約**：URL path 應回傳明確失敗/拒絕狀態（建議非 0 exit code）、`reason_code`（例如 `URL_INPUT_DISABLED`）、使用者可採取的合法替代行動（提供本機音訊、日後合法 allowlist path），並在 `quality_report` 或 CLI stderr/stdout 中保留可測訊息。
- **`arrangement.json` 是共享 schema 契約**：實作不得省略 Test Spec 第 4 節列出的 required 欄位；新增欄位可以是 additive，但不得改名或改變既有欄位語意。
- **警示碼最小集合**：低信心與降級至少需能表示 `LOW_NOTE_CONFIDENCE`、`LOW_CHORD_CONFIDENCE`、`LOW_SECTION_CONFIDENCE`、`LOW_FINGERING_CONFIDENCE`、`UNMAPPED_FINGERING`、`UNPLAYABLE_POSITION`、`AUDIO_ARTIFACT_RISK`、`URL_INPUT_DISABLED`。
- **低信心 hard gate**：低於預設門檻的 note/chord/section/fingering 若沒有對應 warning 或 quality-report entry，MVP 驗收必須失敗。
- **可彈性 hard gate**：`positions[].playability` 只能使用 `playable`、`degraded`、`unplayable`。`unplayable` 不得被渲染成正常 TAB；只能 hard fail，或以明確 `degraded` 狀態降級成 chord-only/文字提示。
- **Golden fixture gate**：三個核心 golden fixtures 與人工 rubric 紀錄是 Phase 0 blocker；沒有合法來源/授權紀錄或 rubric baseline 時，不得宣稱 MVP e2e 通過。
- **非目標鎖定**：alternate tunings、PDF 必備輸出、URL allowlist 實作、DAW 匯出、完整教學、完整歌曲與多樂器通用成功率均不得在 MVP 完成定義中被新增為 blocker。

## 6. 驗收標準

1. 對固定合法 30–90 秒 golden 樣本至少 3 類可產生完整 `tab.md`、`arrangement.json`、`quality_report.json`：簡單和弦刷奏、單音 riff、單音 lead。
2. 輸出包含段落、和弦資訊，以及至少一個可彈 TAB-like guitar part；若只能 chord-only，需明確標示降級原因且不能算通過 riff/lead 必過樣本。
3. 低信心、不可確定、或因分離 artifact 造成的內容會被清楚標示；低信心無 warning 屬 hard fail。
4. 人工驗收判定：作者依 golden fixture rubric 能用輸出練出可辨識版本，而非只得到不可讀 MIDI dump；第二位吉他手建議但非 blocker。
5. 不可彈 TAB 屬 hard fail，包括不存在 string/fret、超出支援 fret 範圍（MVP：0–20）、明顯不可能手位且未降級/警告。
6. 缺少固定 golden fixture 或人工驗收紀錄屬 hard fail。
7. 不要求 DAW export、完整教學、原指法一致、逐音完美、完整歌曲、多樂器混音通用處理。

## 7. 風險與限制

- **YouTube 合規風險**：不得把 MVP 設計成任意下載他人影片；MVP 預設 URL disabled/stub/policy gate。後續合法路徑需 `--i-own-rights`、allowlisted source，或使用者自行提供音訊。
- **範圍膨脹風險**：完整歌曲、混音、多樂器、失真吉他 polyphonic transcription 都容易拖垮 MVP；必過樣本先限制簡單和弦刷奏與單音 riff/lead。
- **音源分離限制**：Demucs 已 archive，6-source guitar/piano experimental 可能 bleed/artifacts；不可把 stem 當真值。
- **polyphonic guitar transcription 難度高**：Basic Pitch 適合單一樂器較佳，混音與失真吉他可能錯漏多。
- **和弦/段落辨識不穩定**：需以信心與人工可修正 artifact 方式呈現。
- **指法非原演奏者**：只能承諾可彈且合理，不承諾原版手法。
- **節奏量化困難**：rubato、shuffle、syncopation 可能導致 TAB 節奏不準。
- **環境依賴**：ffmpeg、MuseScore、Essentia、Demucs、Basic Pitch 版本與 Python 支援需在實作前鎖定。

## 8. Architect / Critic 審查焦點

- 架構是否足夠模組化，避免模型替換時重寫整個系統。
- 初版是否過度依賴 Demucs guitar stem；是否應以 optional enhancement 而非 hard dependency。
- `arrangement.json` 是否足以承載 timebase、source/stem provenance、confidence、warnings、note events、chord spans、section spans、fret/string positions 與 render hints。
- 人工音樂驗收 rubric 是否可重複、可比較。
- YouTube policy gate 是否明確，是否應讓音訊檔成為主路徑。
- Hard fail 條件是否足以阻止「不可彈 TAB」「低信心無 warning」「無固定驗收素材」被誤判為完成。

## 9. 建議後續執行路徑

- Ralph：適合單一路徑完成 greenfield MVP 骨架、樣本、CLI、測試與驗收迭代；開始前確認本 PRD 與 Test Spec 均為最新。
- Team：若要並行，可分四線：架構/資料模型、音訊分析管線、吉他編曲/渲染、測試與驗收素材；需共享 `arrangement.json` schema 與 hard fail 規則。
- Goal mode：若要轉成持久目標，建議 `$ultragoal`；若核心變成模型研究/比較，改用 `$autoresearch-goal`；若效能/速度成為主要瓶頸，再使用 `$performance-goal`。
