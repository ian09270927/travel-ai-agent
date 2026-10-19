# 第一次 Git Commit 與遠端上傳檢查

檢查日期：2026-10-19。範圍為本專案根目錄，沒有加入其他課程資料夾。

## 本地與遠端狀態

- 本地分支：`main`。
- 首次提交訊息：`Initial commit: Taiwan travel AI agent teaching project`。
- 尚未設定 remote、建立 GitHub Repository 或執行 push。
- 建議 GitHub Repository 名稱：`travel-ai-agent`，擁有者與公開／私人設定待使用者確認。
- GitHub CLI 目前顯示既有帳號登入憑證無效，尚未驗證遠端權限。請在自己的終端機使用 `gh auth login -h github.com` 完成登入，勿把密碼、權杖或一次性驗證碼貼進專案或聊天。
- Commit 使用本機既有 Git 作者設定；作者姓名與 Email 會隨提交一併上傳。上傳前請檢查身分與隱私偏好。

## 安全與完整性檢查

對待提交的文字檔，以及 PPTX 內的 XML／關聯檔檢查已知秘密模式：私鑰、GitHub Token、常見 API Key、AWS Access Key、JWT、Bearer Token、含密碼 URL 與明文憑證賦值。未發現符合上述模式的內容。沒有輸出可能的秘密原值。

PNG、MP4 等二進位素材未進行 OCR、聲音辨識或全面人工敏感資訊稽核，不能把模式掃描描述為絕對沒有敏感資訊。這些檔案沿用本專案的 AI 情境圖、教學宣傳片與測試畫面。正式公開前仍需確認素材、文件、Git 作者資料都適合分享。

`.gitignore` 已排除環境設定、憑證與私鑰、依賴、快取、編輯器設定、日誌、中間渲染及製作音訊；保留網站需要的三張圖、最終影片及封面，另保留影片製作腳本與驗證資料。排除檔案仍留在本機。網站不依賴任何秘密設定。

本次不重跑網站功能測試；沒有修改網站功能程式。既有產品驗收結果見 [TEST-REPORT](TEST-REPORT.md)。本次另外檢查版本管理檔案、忽略規則、HTML 本地素材是否納入，以及 Commit 後的工作目錄狀態。

`git diff --cached --check` 僅指出 5 個既有檔案結尾有空白行（測試腳本、CCI、SIPOC、研究來源與 app 腳本）；未為清除格式提示而改動研究原檔或網站程式。

## 完整提交清單

共 **49 個檔案**，約 **33.2 MiB**（未壓縮）。最大單檔為最終 MP4，約 12.7 MiB。

```text
.build/test-site-errors.mjs
.build/test-site.mjs
.gitignore
AGENTS.md
README.md
docs/CCI.md
docs/GIT-HANDOFF.md
docs/PRD.md
docs/SIPOC.md
docs/TEST-REPORT.md
docs/weekly-report.md
index.html
outputs/site-qa/additional-results.json
outputs/site-qa/desktop-full.png
outputs/site-qa/desktop-home.png
outputs/site-qa/landscape-full.png
outputs/site-qa/mobile-form.png
outputs/site-qa/mobile-full.png
outputs/site-qa/mobile-top.png
outputs/site-qa/tablet-form.png
outputs/site-qa/tablet-full.png
outputs/site-qa/test-results.json
outputs/site-qa/text-200.png
outputs/travel-marketing.pptx
research/sources.md
research/travel-data.json
site/app.mjs
site/captions.vtt
site/data/mock-plans.json
site/recommendation.mjs
site/styles.css
slides.html
video/assets_v1/scene-01.png
video/assets_v1/scene-02.png
video/assets_v1/scene-03.png
video/assets_v1/vo-01.srt
video/captions_v1.ass
video/captions_v1.srt
video/final/taiwan-travel-30s-v01.mp4
video/production-v1.md
video/prompts.md
video/render_v1/make-film.py
video/render_v1/playback-validation.json
video/render_v1/previews/frame-02.0.png
video/render_v1/synthesize.ps1
video/render_v1/validation.json
video/storyboard.md
video/watch.html
旅遊情報資料表.md
```

## 上傳前的確認

請確認 GitHub 的擁有者／組織、Repository 名稱、公開或私人、以上檔案是否全部上傳，以及現有儲存庫是否為空。確認後才設定遠端或建立 Repository。若已有遠端內容，應先讀取並比較，不使用 force push 蓋掉既有歷史。

第一次本地提交完成與成功上傳 GitHub 是不同狀態；本文件不代表已經上傳。
