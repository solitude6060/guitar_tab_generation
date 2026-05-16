# P17 PRD：DAW Workflow Usability（DAW 匯出可用性強化）

日期：2026-05-16
狀態：Implemented
Branch：`feature/daw-workflow-usability`

## 1. 背景

P16 已完成 `export --format daw`，可以產出可匯入 GarageBand/Logic 的多軌 bundle。
但產品新手仍需查指令與手動猜測檔案用途。這個階段要把「怎麼用」做進介面與文件。

## 2. 目標

1. 在 `interface.html` 中補上 DAW 匯入頁籤：
   - 顯示 `daw_bundle` 是否存在。
   - 顯示 `daw_bundle` 的 strategy/track 清單。
   - 顯示可直接使用的匯入指引。
2. 在 P16 的 DAW 匯出文件中補齊「快速導入三步驟」。
3. 加入新一輪測試，確保介面 DAW 區塊在「未產生 bundle」與「已產生 bundle」兩種情境正確顯示。
4. 維持零重依賴，不新增外部套件。

## 3. 功能範圍

- `artifact_interface.py`：`interface` 輸出新增/完善 DAW 區塊。
- `tests/unit/test_artifact_interface.py`：單元測試 DAW manifest 與缺失 manifest 的行為。
- `tests/e2e/test_cli_artifact_interface.py`（若必要）：加一個 `interface` + `export --format daw` 的正向 smoke。
- `docs/daw-bundle-export*.md`：補上 `interface.html` 的對應步驟。

## 4. 非目標

- 不修改 `export` 演算法。
- 不加入 GUI 應用（維持離線 HTML / CLI）。
- 不模擬真實 GarageBand / Logic 的 UI 匯入行為。

## 5. 驗收標準

1. 單元測試：
   - `interface` 渲染在未建立 `daw_bundle` 時顯示提示。 
   - `interface` 渲染在有 `daw_bundle/daw_manifest.json` 時顯示 track 列表與策略。
2. 指令測試：
   - `python -m pytest -q tests/unit/test_artifact_interface.py`
   - `python -m pytest -q tests/e2e/test_cli_artifact_interface.py`
3. 文件驗證：
   - `docs/daw-bundle-export.md` 和 `docs/daw-bundle-export.zh-TW.md` 補齊一段可直接引用的匯入步驟。
4. 全量測試通過：`python -m pytest -q`。
