# P38 Project Workspace PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P38 建立多歌曲 Project Workspace，讓 v1.0 使用者能把多個 artifact dir 組成一個 project，保存 song metadata、artifact history 與 workspace index，同時不破壞現有單 `artifact_dir` workflow。

交付：

- 新增 CLI：`guitar-tab-generation workspace init <workspace_dir>`。
- 新增 CLI：`guitar-tab-generation workspace index <workspace_dir>`。
- 新增 CLI：`guitar-tab-generation workspace add-artifact <workspace_dir> <artifact_dir>`。
- workspace schema：`workspace.json`，包含 project metadata、songs、artifact history。
- Web UI artifact browser 讀到 `workspace.json` 時顯示 project name 與 song metadata。

## 2. 非目標

- 不建立雲端同步。
- 不要求所有 artifact 必須在 workspace 內。
- 不改 `transcribe/view/tutorial/interface/export` 的單 artifact_dir 行為。

## 3. 驗收標準

- `workspace --help` 可用。
- `workspace init` 建立 `workspace.json`。
- `workspace index` 可掃描 workspace 下多個 artifact dir 並更新 songs。
- `workspace add-artifact` 可登錄 workspace 外或內的 artifact dir。
- Web UI 在 workspace metadata 存在時顯示 project name。
