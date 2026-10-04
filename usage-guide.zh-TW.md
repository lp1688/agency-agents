# The Agency Agents 使用指南

> 282 個專家 agent 的使用方式 ＋ 多 Agent 接力具體步驟
> 來源：[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)（fork：lp1688/agency-agents）

---

## 一、這些 Agent 是什麼

每個 agent 是一個「專家角色設定檔」：**人格 ＋ 專業知識 ＋ 工作流程 ＋ 交付物模板 ＋ 成功指標**，打包成 system prompt。

載入後，Kimi 就會以該專家的身分、語氣與方法論工作——例如「資安架構師」會用威脅建模的角度看問題、「小紅書專家」會用種草文的邏輯寫文案。工具能力（讀檔、跑指令）不變，變的是「腦袋」。這比叫通用助手「扮演 XXX」效果好得多，因為每個檔案都有完整的工作流程、交付物模板和量化指標。

## 二、目前的安裝狀態

本機已裝好兩種格式，全部 282 個 agent：

| 格式 | 位置 | 用途 |
|------|------|------|
| `agent.yaml` ＋ `system.md` | `~/.config/kimi/agents/<name>/` | 用 `--agent-file` 載入（repo 官方整合格式） |
| 單一 `.md` | `~/.kimi-code/agents/<name>.md` | 用 `--agent <name>` 啟動，或在對話中委派為 sub-agent |

## 三、挑選要用的 Agent

- 用瀏覽器開啟 repo 根目錄的 **`agents-catalog.zh-TW.html`**：依 18 個部門瀏覽，支援中英文搜尋（例如「小紅書」「資安」「react」）
- 或直接看清單：`ls ~/.kimi-code/agents/`

常用入口：

| 需求 | Agent |
|------|-------|
| 寫前端 / 後端 | `frontend-developer` / `backend-architect` |
| 審查程式碼 | `code-reviewer` |
| 資安檢測 | `penetration-tester` / `security-architect` |
| 社群內容 | `xiaohongshu-specialist` / `douyin-strategist` |
| 研究與文獻綜整 | `research-synthesist` |
| 產品規劃 | `product-manager` / `product-manager-senior` |

## 四、基本使用方式

### 1. 互動模式（整個 session 都用這個人格）

```bash
kimi --agent frontend-developer
```

### 2. 單次執行（適合腳本或快速問答）

```bash
kimi -p "幫我 review 這個分支的改動" --agent code-reviewer
```

### 3. 在專案目錄裡用（agent 才能操作你的程式碼）

```bash
cd /your/project
kimi --agent backend-architect
```

### 4. 用 repo 官方格式（agent.yaml）

```bash
kimi --agent-file ~/.config/kimi/agents/frontend-developer/agent.yaml
```

### 重要規則

- **一個 session 一個角色**：agent 在 session 建立時綁定，中途不能換
- `kimi --continue` 或 `kimi --session` 續聊時會**自動沿用**原本綁定的 agent，不需（也不能）再下 `--agent`
- 想換角色 → 開新 session

---

## 五、多 Agent 接力：具體步驟

### 核心概念

> **每個角色開一個 session，用「檔案」當交接棒。**

session 之間看不到彼此的聊天記錄，唯一溝通管道是專案裡的檔案。

### 範例：一天做完 Landing Page（4 個 agent 接力）

**第 0 步：建專案，規劃交接文件**

```bash
mkdir flowsync-landing && cd flowsync-landing
```

| 棒次 | Agent | 產出檔 |
|------|-------|--------|
| 1 文案 | `content-creator` | `docs/01-copy.md` |
| 2 設計 | `ui-designer` | `docs/02-design.md` |
| 3 實作 | `frontend-developer` | `index.html` |
| 4 優化 | `growth-hacker` | 直接改 `index.html` |

**第 1 棒：文案**

```bash
kimi --agent content-creator
```

進入後下指令（**關鍵：要求把產出寫成檔**）：

```
為 FlowSync（API 整合平台，5 分鐘串起任意兩個 SaaS）寫 landing page 文案。
目標受眾：中型公司的開發者和技術 PM。語氣：自信、簡潔、微幽默。
需要：Hero、痛點×3、運作方式×3、社會證明、三層定價、結尾 CTA。
完成後把全文存到 docs/01-copy.md。
```

**第 2 棒：設計**（可與第 1 棒同時開另一個終端機平行跑）

```bash
kimi --agent ui-designer
```

```
讀 docs/01-copy.md，為這個 SaaS landing page 出設計規格
（Linear/Vercel 風格、深色模式）：版面線框、色票、字體搭配、
元件規格（hero/卡片/定價表/CTA）、響應式斷點。
存到 docs/02-design.md。
```

**第 3 棒：實作**

```bash
kimi --agent frontend-developer
```

```
讀 docs/01-copy.md 和 docs/02-design.md，用 HTML + Tailwind +
少量 vanilla JS 做出 index.html：行動優先、無障礙、
含 email 註冊表單（action=/api/subscribe）。
```

**第 4 棒：轉化優化**

```bash
kimi --agent growth-hacker
```

```
讀 index.html，從轉化率角度提出 3–5 個問題並直接修改：
CTA 文案、社會證明位置、表單阻力、行動版體驗。
```

**需要改其中一棒？** 回到該角色的 session 續聊，它的記憶還在：

```bash
cd flowsync-landing
kimi --session      # 從清單選回 content-creator 那個 session
```

### 接力三規則

1. **交接物是檔案，不是對話**——下一棒完全不知道上一棒聊過什麼，指令裡一定要寫「讀 docs/xx.md」
2. **每棒產出要明確落地**——指令結尾加「存到 docs/yy.md」，不要讓產出只留在對話裡
3. **同角色迭代用 `--session` 回去**——跨角色才開新 session

### 現成劇本（可直接抄）

- `examples/workflow-landing-page.md` — 上面的完整版
- `examples/workflow-startup-mvp.md` — 新創 MVP
- `examples/workflow-book-chapter.md` — 寫書章節
- `strategy/playbooks/`、`strategy/runbooks/` — 更大規模的多 agent 編排

## 六、進階：單一 Session 內自動接力（Sub-agent 委派）

282 個 agent 已裝進 `~/.kimi-code/agents/`，所以直接開 `kimi`（不帶 `--agent`），主 agent 會依任務**自動委派**給這些專家；也可以明示：

```
用 product-manager 把這個想法寫成 PRD 存到 docs/prd.md，
然後用 ui-designer 讀 prd 出設計規格，
最後用 frontend-developer 實作。
```

每個 sub-agent 在獨立 context 工作，只把最終結果交回主 agent——主對話不會被探索過程洗版，多個 sub-agent 還能平行執行。

> 同步方式：上游更新後重跑 `python scripts/gen-kimi-subagents.py` 即可更新這批 sub-agent。

## 七、給其他 AI 工具用

這個 repo 支援 17 種工具（Claude Code、Cursor、Codex、Gemini CLI⋯⋯）：

```bash
./scripts/convert.sh --tool cursor
./scripts/install.sh --tool cursor
```

最簡單的通用法：把 agent 的 `.md` 原始檔內容貼進任何 AI 工具的 system prompt 或專案指令檔（如 `AGENTS.md`），人格立即生效。

## 八、常見問題

**Q：agent 沒有照預期角色回應？**
確認啟動指令沒打錯名字；`kimi --agent 不存在的名字` 會列出全部可用名稱。

**Q：續聊時角色消失了？**
不會。resume 會自動還原綁定的 agent；但 `--agent` / `--agent-file` 不能和 `--session` / `--continue` 並用。

**Q：上游出了新 agent 怎麼同步？**

```bash
git pull origin main
./scripts/convert.sh --tool kimi && ./scripts/install.sh --tool kimi
python scripts/gen-kimi-subagents.py
python scripts/gen-html-catalog.py && python scripts/gen-html-catalog.py --lang zh-TW
```

---

*本文件由 lp1688/agency-agents fork 產出；參考：[Kimi Code — Agents and Sub-Agents](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents.html)、[kimi 命令列參數](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command.html)*
