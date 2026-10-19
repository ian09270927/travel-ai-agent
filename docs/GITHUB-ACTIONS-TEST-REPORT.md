# GitHub Actions 旅遊週報示範｜驗收紀錄

日期：2026-10-19。狀態：**已真實手動執行兩次 GitHub Actions：fixture 成功；live 因來源回傳非 ZIP 頁面而失敗停止。兩次 artifact 均已下載核對。週一 schedule 投遞仍未驗證；AI、網站寫回、發布皆未實作。** 執行方式及來源授權見 [示範說明](GITHUB-ACTIONS-DEMO.md)。

## 分層結果

| 層次 | 本次結果 | 不能據此宣稱的事 |
|---|---|---|
| 排程檔與權限 | YAML 解析通過；cron=`0 1 * * 1`，時間換算測試為台北週一 09:00；contents:read，GitHub 已接受工作流程並完成手動 runner／artifact 步驟 | 手動 workflow_dispatch 不等於真實週一 schedule 投遞 |
| 本地程式 | 15 個 Python unittest 通過；固定資料沒有網路呼叫 | 不是 live 來源成功，也不是 AI 推論 |
| fixture 端到端 | 6 筆輸入、3 筆候選、2 筆去重、1 筆無效；待審稿及紀錄產生成功 | 全部為測試資料，不是真實景點研究 |
| 真實公開資料快照 | 首次探查成功下載現行 ZIP，原始 6,185 筆，解析去重後 6,072 筆、去重 113 筆、無效 0 | 後續只使用快照測解析，不代表本次 live 全流程成功；沒有跨週增量比較 |
| 本地 live 嘗試 | 詮釋資料頁通過授權文字與連結檢查，但下載回 HTTP 200／419 bytes 的 Request Rejected HTML；流程 exit 1，沒有生成週報 | 不可宣稱來源當時可下載、內容已驗證或週報成功 |
| GitHub fixture 真實執行 | 15 個單元測試、collector、job summary、artifact 上傳成功；下載確認 6 筆輸入／3 筆候選／2 筆重複／1 筆無效 | 測試資料成功不等於 live 取得資料 |
| GitHub live 真實執行 | runner／15 個測試成功；來源詮釋資料檢查通過，ZIP 端點回 HTML，collector exit 1；summary 與失敗 artifact 正常保存 | live 全流程仍失敗，不改名為成功、不用 fixture 補成旅遊週報 |
| 人工審稿 | 草稿有 pending_review、署名、未核對事項及核對清單 | 尚無審稿人核准 |
| AI | not_used，沒有 API Key、沒有付費模型呼叫 | 尚無 AI 品質、模型權限、費用或速率驗證 |
| 網站更新／發布 | not_attempted，沒有部署及網站寫回步驟 | 程式成功不等於網站已更新或上線 |

## 證據檔案

### 真實 GitHub 手動執行

兩次均使用提交 `b5e47c956ebec4384a4e745fcc2e620395568beb`、事件 `workflow_dispatch`，無等待週一、無修改 cron：

- [fixture 成功 Run 39256563133](https://github.com/ian09270927/travel-ai-agent/actions/runs/39256563133)，台北時間 2026-10-19 21:00 建立並執行。
- [live 失敗 Run 39256597404](https://github.com/ian09270927/travel-ai-agent/actions/runs/39256597404)，台北時間 2026-10-19 21:01 建立並執行。
- [兩次 Run／Job／Artifact 的 GitHub metadata](automation-evidence/github-runs.json)。
- [GitHub fixture 摘要](automation-evidence/github-fixture-run.json)、[待審稿](automation-evidence/github-fixture-report.pending.md)、[事件紀錄](automation-evidence/github-fixture-events.ndjson)。
- [GitHub live 失敗摘要](automation-evidence/github-live-run.json)、[HTTP 及阻擋事件](automation-evidence/github-live-events.ndjson)。

下載產物後已核對事件、run ID、模式、commit SHA、fixture 計數，以及兩次 AI／網站／發布欄位。live 沒有 weekly-report.pending.md；沒有繞過來源站拒絕或偽造查詢成果。

### 先前本地測試與來源探查

- [本地測試結果與案例](automation-evidence/local-tests.json)。15 案例包括時區、無網路 fixture、去重較新資料／別名、共用官網不誤合併、缺地址不誤合併、壞資料、URL 安全、來源白名單、授權／資源連結檢查、ZIP 指定成員／格式漂移、失敗紀錄、受保護路徑與禁止覆寫、模擬 live 傳輸，以及 HTTP 200 拒絕頁直接停止。
- [fixture 執行摘要](automation-evidence/fixture-run.json)、[待審核週報範例](automation-evidence/fixture-report.pending.md)。
- [真實快照解析／去重檢查](automation-evidence/source-snapshot-check.json)。原快照擷取時間未另存，證據不補造查詢日期；保留來源更新時間及原 ZIP SHA-256。
- [live 失敗摘要](automation-evidence/live-attempt.json)、[HTTP 與階段事件紀錄](automation-evidence/live-events.ndjson)。

live 失敗是初版解析時偵測到 BadZipFile，當時的 `source_check` 字串僅代表 metadata／HTTP 已檢查，不能解讀為有效資料下載成功。後續已修正：ZIP 簽章不符即辨識來源拒絕／非預期內容，停止且不重試繞過；來源檢查只有 JSON 解析完成後才標為完整成功。新行為由回歸測試確認，沒有為重測而繞過來源封鎖。

測試初次曾因 Windows 沙箱暫存目錄權限失敗；已將單元測試暫存限制在專案忽略的 `.build/actions-demo/tests/`，重跑 15 案例通過。測試沒有修改產品資料。

## 原檔與範圍保護

`git diff --name-only` 未包含 index.html、site/、research/ 或既有週報；原研究 JSON／sources.md 雜湊與前階段相同。已提交並推送自動化程式、工作流程、說明／證據，以及在 `.gitignore` 排除執行產物。先前尚未提交的技能與 README 內容保留，未一併 Commit 或 push。

已驗收 GitHub 手動 fixture 與 live 失敗紀錄保存；下一步是處理來源允許連線的可用性、重驗 live 成功路徑，以及觀察真實 schedule 事件。人工審稿與網站變更仍是獨立階段，只有明確授權網站更新時才執行。不能把本地模擬、遠端手動執行、排程或發布混為一項成功。
