# ADR 目錄

本目錄保存 Architecture Decision Records。任何會影響架構、依賴、輸入政策、輸出 schema、模型選擇、或合法 URL 支援策略的改動，都應先新增 ADR，再進入實作。

命名：`YYYYMMDD-short-title.md`

建議模板：

```markdown
# ADR-YYYYMMDD：<決策標題>

## 狀態

Proposed / Accepted / Superseded

## 背景

為什麼需要這個決策？目前限制是什麼？

## 決策

我們決定採用什麼方案？

## 替代方案

- 方案 A：優點 / 缺點 / 拒絕原因
- 方案 B：優點 / 缺點 / 拒絕原因

## 後果

正面、負面、維護成本、回滾方式。

## 驗證

如何用測試、fixture、人工驗收或文件確認這個決策有效？
```
