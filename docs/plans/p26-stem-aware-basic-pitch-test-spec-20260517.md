# P26 Test Spec：Stem-aware Basic Pitch Pipeline

日期：2026-05-17
狀態：Planned

## 1. Unit tests

- `tests/unit/test_stem_manifest_reader.py`
  - 可讀取 `stem_manifest.json` 並解析指定 stem path。
  - stem path 不存在時失敗。
  - stem path 跑出 artifact directory 時失敗。
  - 指定 stem 不存在時失敗並列出可用 stem names。
- `tests/unit/test_basic_pitch_backend.py`
  - fake Basic Pitch predict 產生 note events 時，指定 `stem_name=guitar` 會把 provenance 寫為 `stem: guitar`。
  - 未指定 stem 時仍保持 `stem: mix`。

## 2. E2E tests

- `tests/e2e/test_cli_transcribe_stem.py`
  - `transcribe-stem --help` 顯示 `--stem` 與 `--backend`。
  - fake artifact directory 含 `stem_manifest.json` 與 `stems/guitar.wav` 時，CLI 產生 `stem_notes/guitar.notes.json`。
  - 缺少 manifest 時回傳錯誤並提示先跑 `separate-stems`。
  - `transcribe --help` 仍沒有 `--stem`。

## 3. Manual demo gate

P26 default 不跑真實 Demucs，也不要求真實 Basic Pitch。manual gate 先用 P25 fake artifact contract 或測試 fixture；若要真實 Basic Pitch，必須明確安裝 optional `ai` group 並記錄為 manual smoke，不進 default CI。

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe-stem /tmp/guitar-tab-p25 --backend basic-pitch --stem guitar --help
```

## 4. Regression gates

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe-stem --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe --help
```

## 5. Red-first expectations

第一個 red test 應鎖定 `transcribe-stem --help` 或 stem manifest reader 不存在。第二個 red test 鎖定 provenance 不得默認 `mix`。

