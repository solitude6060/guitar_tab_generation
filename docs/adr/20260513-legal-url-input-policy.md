# ADR-20260513：Legal URL Input Policy

## 狀態

Accepted for future design; implementation remains disabled in MVP.

## 背景

產品願景包含貼上 YouTube/URL 後自動產生吉他譜，但 MVP 目前是 local-audio-first。任意 URL 下載會引入版權、平台條款、使用者權利聲明、暫存媒體、審計與濫用風險。因此 arbitrary URL download remains disabled，直到另有合法輸入流程與明確測試。

## 決策

MVP 維持：

- arbitrary URL download remains disabled。
- URL/YouTube 輸入只走 policy gate，輸出明確拒絕訊息。
- `--i-own-rights` 在目前 MVP 不會啟用任意 URL 下載，也不會繞過 policy gate。
- 合法替代路徑是 user-provided audio：使用者自行提供合法本機 30–90 秒音訊。

未來若要支援 URL，必須同時滿足：

1. **allowlist**：只允許明確受控來源，例如自有 storage、測試 fixture server、或已批准 provider。
2. **rights attestation**：使用者必須明確聲明擁有權利或授權，且不能只用單一 flag 默默繞過。
3. **audit log**：記錄 URL、rights attestation、allowlist decision、時間、輸出 artifact provenance。
4. **provenance**：`arrangement.json.source` 必須標記 URL policy decision 與使用者提供/allowlisted 來源。
5. **no silent download**：下載前必須先通過 policy gate；失敗不得建立音訊 artifact。

## 替代方案

- 方案 A：MVP 直接支援任意 YouTube URL。  
  拒絕原因：版權/平台條款風險過高，且非核心 transcription MVP 必要條件。
- 方案 B：只要 `--i-own-rights` 就允許任意 URL。  
  拒絕原因：缺少 allowlist、audit log 與 provenance，容易被誤用成下載器。
- 方案 C：維持 local-audio-first，未來另開 allowlisted URL path。  
  採用原因：保留產品方向，同時不破壞 MVP 合規邊界。

## 後果

- 使用者目前必須提供合法本機音訊。
- 未來 URL 支援會需要額外 UI/CLI 文案、audit log、allowlist 設定與測試。
- 任何實作 URL 下載的 PR 都必須先更新本 ADR 或新增 superseding ADR。

## 驗證

- `tests/test_url_policy_guard.py` 確認 `--i-own-rights` 不會啟用 arbitrary URL download。
- URL policy gate 不得產生 `audio_normalized.wav`、`arrangement.json`、`quality_report.json`、`tab.md`、`notes.json`、`chords.json`、`sections.json`。
- ADR contract test 確認文件包含 allowlist、rights attestation、audit log 與 user-provided audio requirements。
