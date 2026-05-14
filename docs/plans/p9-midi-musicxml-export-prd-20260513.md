# P9 PRD：MIDI / MusicXML Export MVP

日期：2026-05-13
狀態：Implemented
Branch：`feature/midi-musicxml-export`

## 1. 背景

原始產品願景包含 GarageBand / Logic Pro 匯入。P5 research 決定不要直接產生專有 DAW session，而是先做通用交換格式：MIDI 與 MusicXML。

## 2. 目標

新增 CLI：

```bash
guitar-tab-generation export <artifact_dir> --format musicxml --out score.musicxml
guitar-tab-generation export <artifact_dir> --format midi --out score.mid
```

匯出只讀既有 artifacts，不重新執行 transcription。

## 3. 功能需求

1. `export` command 接受 artifact directory。
2. `--format` 支援 `musicxml` 與 `midi`。
3. MusicXML 必須包含 pitch、duration、measure/part 結構，以及 confidence/warning metadata。
4. MIDI 必須產生標準 `MThd`/`MTrk` 檔頭與 note on/off events。
5. 缺必要 artifact 時回傳非 0，不產生誤導性成功檔案。
6. 不下載 URL，不產生 DAW 專有 session。

## 4. 非目標

- 不做 GarageBand / Logic Pro 專案檔。
- 不做多軌 source separation。
- 不保證專業譜面排版；這是 artifact exchange MVP。

## 5. Definition of Done

實作狀態：已完成。CLI `export`、MusicXML/MIDI unit/e2e tests、uv regression、manual demo gate 已通過。

- PRD + test spec 存在。
- 先新增 failing tests，再實作。
- 三個 golden fixtures 可匯出 MusicXML 與 MIDI。
- `uv run pytest -q` 通過。
- `uv run guitar-tab-generation export --help` 通過。
- Feature 經 code review 後 merge `dev`，驗證，再 merge `main`。
