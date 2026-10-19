# GitHub Actions 旅遊週報示範｜驗收紀錄

日期：2026-10-19。狀態：**本地管線與失敗處理已測；現正依使用者授權進行遠端手動測試，結果完成後補於本文件；週一 schedule 投遞仍未驗證；AI、網站寫回、發布皆未實作。** 執行方式及來源授權見 [示範說明](GITHUB-ACTIONS-DEMO.md)。

## 分層結果

| 層次 | 本次結果 | 不能據此宣稱的事 |
|---|---|---|
| 排程檔與權限 | YAML 解析通過；cron=`0 1 * * 1`，時間換算測試為台北週一 09:00；contents:read，含手動 fixture/live | 尚未驗證 GitHub schema、runner 執行、artifact 上傳或真實週一投遞 |
| 本地程式 | 15 個 Python unittest 通過；固定資料沒有網路呼叫 | 不是 live 來源成功，也不是 AI 推論 |
| fixture 端到端 | 6 筆輸入、3 筆候選、2 筆去重、1 筆無效；待審稿及紀錄產生成功 | 全部為測試資料，不是真實景點研究 |
| 真實公開資料快照 | 首次探查成功下載現行 ZIP，原始 6,185 筆，解析去重後 6,072 筆、去重 113 筆、無效 0 | 後續只使用快照測解析，不代表本次 live 全流程成功；沒有跨週增量比較 |
| 本地 live 嘗試 | 詮釋資料頁通過授權文字與連結檢查，但下載回 HTTP 200／419 bytes 的 Request Rejected HTML；流程 exit 1，沒有生成週報 | 不可宣稱來源當時可下載、內容已驗證或週報成功 |
| 人工審稿 | 草稿有 pending_review、署名、未核對事項及核對清單 | 尚無審稿人核准 |
| AI | not_used，沒有 API Key、沒有付費模型呼叫 | 尚無 AI 品質、模型權限、費用或速率驗證 |
| 網站更新／發布 | not_attempted，沒有部署及網站寫回步驟 | 程式成功不等於網站已更新或上線 |

## 證據檔案

- [本地測試結果與案例](automation-evidence/local-tests.json)。15 案例包括時區、無網路 fixture、去重較新資料／別名、共用官網不誤合併、缺地址不誤合併、壞資料、URL 安全、來源白名單、授權／資源連結檢查、ZIP 指定成員／格式漂移、失敗紀錄、受保護路徑與禁止覆寫、模擬 live 傳輸，以及 HTTP 200 拒絕頁直接停止。
- [fixture 執行摘要](automation-evidence/fixture-run.json)、[待審核週報範例](automation-evidence/fixture-report.pending.md)。
- [真實快照解析／去重檢查](automation-evidence/source-snapshot-check.json)。原快照擷取時間未另存，證據不補造查詢日期；保留來源更新時間及原 ZIP SHA-256。
- [live 失敗摘要](automation-evidence/live-attempt.json)、[HTTP 與階段事件紀錄](automation-evidence/live-events.ndjson)。

live 失敗是初版解析時偵測到 BadZipFile，當時的 `source_check` 字串僅代表 metadata／HTTP 已檢查，不能解讀為有效資料下載成功。後續已修正：ZIP 簽章不符即辨識來源拒絕／非預期內容，停止且不重試繞過；來源檢查只有 JSON 解析完成後才標為完整成功。新行為由回歸測試確認，沒有為重測而繞過來源封鎖。

測試初次曾因 Windows 沙箱暫存目錄權限失敗；已將單元測試暫存限制在專案忽略的 `.build/actions-demo/tests/`，重跑 15 案例通過。測試沒有修改產品資料。

## 原檔與範圍保護

`git diff --name-only` 未包含 index.html、site/、research/ 或既有週報；原研究 JSON／sources.md 雜湊與前階段相同。這次只有新增自動化程式、工作流程、說明／證據，以及在 `.gitignore` 排除執行產物。先前尚未提交的技能與 README 內容保留，未一併 Commit 或 push。

接下來的獨立驗收是「GitHub 手動 fixture → GitHub 手動 live → 真實 schedule 事件 → 人工審稿」；只有後續明確授權網站更新時，才另驗收網站變更。此紀錄沒有把本地模擬、真實連線嘗試、排程或發布混為一項成功。
