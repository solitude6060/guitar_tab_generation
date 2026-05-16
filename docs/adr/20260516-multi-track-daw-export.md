# ADR-20260516：Multi-track DAW export via deterministic per-chunk bundle

## 狀態

Accepted

## 背景

產品已具備 `musicxml` 與 `midi` 匯出。P11 已建立 full-song `chunked_full_song` processing plan，但尚未把轉譯結果組織成可直接導入 DAW 的工作流。若直接輸出單一長檔，full-song 導入會難以對齊後製處理。

## 決策

新增 `--format daw` 的輸出格式，輸出一個 bundle 目錄：

- clip: 單 track。
- full-song 且 chunked plan: 每段一 track。
- 每 track 同時輸出 `mid` + `musicxml`，搭配 `daw_manifest.json` 與 `DAW_IMPORT_README.md`。

## 替代方案

- 方案 A：直接輸出單一 `score.mid` / `score.musicxml`，不輸出 bundle。  
  - 優點：實作最少。
  - 缺點：無法對應 full-song chunk 逐段導入 DAW；不利於後續多軌實作。

- 方案 B：直接生成 GarageBand / Logic 專案檔。  
  - 優點：理想端到端使用體驗。  
  - 缺點：格式封閉、依賴高、難以長期維護，且目前不符「先用通用交換格式」路線。

## 後果

- 正向：對 full-song 工作流程友好，bundle 可直接被 GarageBand / Logic 匯入為多軌素材。
- 成本：多筆檔案輸出與清單文件需要維護。
- 回滾方式：可直接退回 `--format midi` / `--format musicxml`，停止使用 `daw`。

## 驗證

- P16 單元與 e2e tests。
- `daw_manifest.json` 可檢查 track 數、策略與 window。
- `DAW_IMPORT_README.md` 提供可操作導入指引。
