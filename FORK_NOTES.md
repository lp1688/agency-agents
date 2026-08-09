# Fork 變更紀錄（lp1688/agency-agents）

本 fork 基於上游 [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)，以下為本 fork 額外新增的檔案（相對於上游 `main`）。

## 新增檔案

| 檔案 | 說明 |
|------|------|
| `agents-catalog.html` | 全部 270 個 agent 的英文目錄（依 17 個 division 分類，含搜尋與導覽） |
| `agents-catalog.zh-TW.html` | 繁體中文版 agent 目錄（中文名稱＋英文原名並列，雙語搜尋） |
| `contributing-guide.zh-TW.html` | 繁體中文貢獻指南：新增 / 優化 agent 的完整規範、CI 檢查、PR 流程與常見地雷 |
| `scripts/gen-html-catalog.py` | 目錄產生器；`--lang zh-TW` 時套用譯文產出中文版 |
| `i18n_chunks/chunk0..4.json` | 由 agent frontmatter 抽出的原文資料（5 份，供翻譯用） |
| `i18n_chunks/chunk0..4.zh-TW.json` | 對應的繁體中文譯文（翻譯記憶，新增 agent 時可增量補譯） |

## 重新產生方式

```bash
# 上游更新後重新產生英文目錄
python scripts/gen-html-catalog.py

# 重新產生繁中目錄（若有新增 agent，需先在 i18n_chunks/ 補譯文）
python scripts/gen-html-catalog.py --lang zh-TW
```

## 同步上游

```bash
git pull origin main      # origin = 上游 msitarzewski/agency-agents
git push fork main        # fork   = 本 fork lp1688/agency-agents
```
