# v1.0 MVP Completion Test Spec

日期：2026-05-18
狀態：Planned

## 1. 全域測試原則

- default CI 不下載 heavy models，不跑 GPU，不執行真實 URL 下載。
- 所有 AI sidecars 使用 deterministic/fake runtime 測試。
- 每個 artifact sidecar 必須有 provenance、confidence、warnings。
- 低 confidence 不得 silent pass。
- UI / workspace / setup 只能讀 artifacts 或呼叫 CLI/service boundary。

## 2. P28-P40 必測清單

| Phase | Required tests |
|---|---|
| P28 | `chord-detect --help`、`chords.json` schema、low-confidence warning、viewer/interface chord summary |
| P29 | `section-detect --help`、`sections.json` schema、boundary confidence、viewer/interface section summary |
| P30 | fingering cost model unit tests、max-stretch warning、golden riff snapshot |
| P31 | fake LLM prompt builder、artifact citation checks、missing runtime failure |
| P32 | Web UI upload/job/artifact browser contract tests |
| P33 | fake GPU probe、queue lock、cancel/resume/logs tests |
| P34 | no-rights URL block、unsupported URL block、source policy record |
| P35 | eval manifest rights/rubric checks、metrics report thresholds |
| P36 | DAW manifest v2、tempo markers、track naming tests |
| P37 | model cache list/doctor/prune dry-run tests |
| P38 | workspace index, multi-song metadata, single artifact_dir compatibility |
| P39 | setup dry-run, docker compose config, dependency doctor |
| P40 | release checklist, docs links, clean clone smoke, security/legal review |

## 3. Final Regression Gate

```bash
uv sync --group dev
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
```

CLI help gate：

```bash
uv run guitar-tab-generation --help
uv run guitar-tab-generation transcribe --help
uv run guitar-tab-generation chord-detect --help
uv run guitar-tab-generation section-detect --help
uv run guitar-tab-generation quality-report --help
uv run guitar-tab-generation export --help
```

## 4. Release Evidence

P40 must produce `docs/reviews/v1-release-readiness-YYYYMMDD.zh-TW.md` with:

- all P28-P40 statuses,
- PR numbers,
- merge SHAs,
- CI runs,
- local verification commands,
- known limitations,
- non-goals preserved for post-v1.0.
