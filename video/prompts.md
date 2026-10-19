# 30 秒台灣旅遊宣傳片｜可複製生成提示詞

配套：[分鏡、旁白、字幕與來源](storyboard.md)。共 3 段，每段目標 10 秒，16:9。所有人物均為虛構，場景為氛圍示意，不能冒充真實景點實拍。

## 本次可執行狀態

本機 Higgsfield CLI 存在，但帳戶狀態回傳未登入，因此可用影片模型、額度與費用均未查得。本次沒有送出生成工作，也沒有輸出影片、角色圖片或音訊。Higgsfield／Runway 連接器搜尋結果為未安裝；可在未來完成連接後重新查詢。

以下是可貼入支援文字或參考圖影片生成器的自然語言提示詞，不是已驗證的 API 參數。採單鏡頭、單一主要運鏡的提示結構，適合逐段製作。若平台提供 Kling 等選項，仍須先以當時模型清單、時長與參考圖介面為準；本文件不宣稱目前帳號已可使用特定模型或免費額度。

## 先建立共同角色與視覺參考

使用以下人物圖提示詞，先生成並挑選四位虛構演員。將確認後的角色圖存為 `REF-A.png` 至 `REF-D.png`；檔名只是製作代號，本次尚無這些圖片。

### 人物 A｜三段固定女主角

```text
Create an original fictional Taiwanese woman aged 35, oval face, dark brown eyes, straight shoulder-length black hair tucked behind her left ear. Cream linen overshirt over a forest-green top, khaki trousers, ivory flat shoes, canvas tote with a burnt-orange scarf. Neutral standing pose, front and three-quarter views, plain warm-gray background, soft diffused daylight, natural skin texture, realistic proportions, 50mm portrait perspective. No text, no logos, no celebrity likeness. Keep the same face and outfit for all later scenes.
```

### 人物 B｜孩子

```text
Create an original fictional Taiwanese girl aged 8, black ponytail, burnt-orange cotton top, light-khaki trousers, white sneakers. Neutral relaxed standing pose, front and three-quarter views, plain warm-gray background, soft diffused daylight, natural skin texture, realistic child proportions, 50mm portrait perspective. No text, no logos, no celebrity likeness. Keep this face and outfit fixed in later scenes.
```

### 人物 C｜伴侶

```text
Create an original fictional Taiwanese man aged 36, short black hair, navy-blue shirt, sand-colored trousers, ivory flat shoes. Neutral relaxed standing pose, front and three-quarter views, plain warm-gray background, soft diffused daylight, natural skin texture, realistic proportions, 50mm portrait perspective. No text, no logos, no celebrity likeness. Keep this face and outfit fixed in later scenes.
```

### 人物 D｜熟齡母親

```text
Create an original fictional Taiwanese woman aged 65, short salt-and-pepper hair, sage-green light jacket over a cream top, dark-gray trousers, flat shoes. Natural age detail, relaxed upright posture without exaggerated frailty. Front and three-quarter views, plain warm-gray background, soft diffused daylight, natural skin texture, realistic proportions, 50mm portrait perspective. No text, no logos, no celebrity likeness. Keep this face and outfit fixed in later scenes.
```

角色確認後，先建立三個場景首幀，將人物圖指定到平台的角色或參考圖欄位；不要假設輸入檔名就會自動附圖。每次保持同一組 A 圖、髮型、鞋子與絲巾位置。若只有首幀圖生影片功能，先把角色合成到場景首幀，再轉動態。

共同視覺：深綠 `#123E32`、奶油白 `#F8F3E7`、暖橘 `#E7834F`。35mm 視角、柔和側逆光、自然膚色、低對比高光、細緻顆粒、克制表演。色碼是造型與後製方向，不要求把真實湖水或植物改成固定色塊。

## 第 1 段｜00:00–00:10｜母女探索

**附圖：** REF-A、REF-B；或已確認含兩人的 FRAME-01 首幀。

**文字／角色參考模式提示詞：**

```text
Taiwan urban park, leafy path beside a softly visible pond. The same fictional Taiwanese mother from reference A, cream linen overshirt and green top, accompanies the child from reference B. The child points toward a leaf beside the path; the mother gently leans to observe, both remaining on the walkway. One continuous eye-level 35mm lateral tracking shot, left-to-right movement, soft warm rim light, natural skin tones, restrained highlights, subtle film grain, quiet travel-commercial mood. Ten seconds, 16:9. Silent picture, no text or logos.
```

**已有首幀時的精簡動態提示詞：**

```text
Preserve the exact faces, clothing and park layout in the start frame. The child points toward a leaf beside the path and the mother gently leans to observe. Both stay on the walkway. A single slow eye-level lateral tracking move follows left to right. Natural body motion, stable daylight, no scene cuts, no face changes. Ten seconds, 16:9, silent picture with no text or logos.
```

**另錄旁白：**「帶孩子看看自然，讓好奇心，成為旅行的起點。」

**後製：** 鋼琴與木吉他輕入，少量鳥鳴。片尾字卡「一起探索」。00:10 以同方向動作直接剪至段 2。

**設計理由：** 單一側向跟拍、眼平 35mm、柔和側逆光、自然膚色、克制高光與顆粒共同形成攝影感；只安排「指向、俯身觀看」這一組簡單互動，減少手部與人物混亂。

## 第 2 段｜00:10–00:20｜伴侶相處

**附圖：** 同一份 REF-A、REF-C；或已確認含兩人的 FRAME-02 首幀。

**文字／角色參考模式提示詞：**

```text
A quiet Japanese-style timber courtyard in Taiwan, an illustrative setting without identifiable landmark reconstruction. The same fictional Taiwanese woman from reference A, unchanged face and cream-and-green outfit, walks beside the partner from reference C along a timber veranda. They exchange one relaxed smile while moving left to right. One continuous eye-level 35mm lateral tracking shot, soft warm rim light, natural skin tones, restrained highlights, subtle film grain, intimate travel-commercial mood. Ten seconds, 16:9. Silent picture, no text, signs or logos.
```

**已有首幀時的精簡動態提示詞：**

```text
Preserve the exact faces, clothing and courtyard layout in the start frame. The couple walks slowly side by side from left to right and exchanges one relaxed smile. A single eye-level lateral tracking move maintains their pace. Keep natural expressions, stable warm daylight and realistic body movement. No scene cuts, no morphing, no speech. Ten seconds, 16:9, silent picture with no text or logos.
```

**另錄旁白：**「和喜歡的人，走進庭園與文化，留一點時間，好好相處。」

**後製：** 延續同首配樂並加入輕弦樂，木廊腳步聲低量。片尾字卡「共享體驗」。00:20 直接剪到段 3，人物動向連續。

**設計理由：** 沿用段 1 的焦段、運鏡與光質，以固定造型和同向行走建立一致性。只更換相處對象與場景，不增加換裝、第二場景或複雜表演。

## 第 3 段｜00:20–00:30｜母女慢遊與結尾

**附圖：** 同一份 REF-A、REF-D；或已確認含兩人的 FRAME-03 首幀。

**文字／角色參考模式提示詞：**

```text
An illustrative Taiwan lakeside walkway, open water and green shoreline, no identifiable platform architecture. The same fictional Taiwanese woman from reference A, unchanged cream-and-green outfit, accompanies the older woman from reference D at a comfortable pace. They stop and look across the lake. Keep both figures on the left third, clean negative space on the right. One continuous slow eye-level 35mm dolly-in, soft warm rim light, natural skin tones, restrained highlights, subtle film grain. Ten seconds, 16:9. Silent picture, no titles, signs or logos.
```

**已有首幀時的精簡動態提示詞：**

```text
Preserve the exact faces, clothing and lakeside layout in the start frame. The two women take a few comfortable steps, then stop and look across the lake. Keep them in the left third and preserve empty space on the right for later titles. A single slow eye-level dolly-in continues smoothly. Stable warm daylight, natural body motion, no scene cuts, no face changes. Ten seconds, 16:9, silent picture with no text or logos.
```

**另錄旁白：**「陪家人照自己的步調旅行。告訴我們日期與偏好，一起討論安排。」

**後製：** 27.5–30 秒在右側留白加入「台灣旅行，從喜歡的事開始」與「告訴我們日期與偏好」。讓旁白字幕維持底部獨立區域。配樂結尾收束，保留水與風的輕微環境音，不生成假電話、網址或 QR code。

**設計理由：** 最後一段只做慢速推近，以左側人物與右側負空間服務 CTA。沒有讓演員說話，因此旁白可保持同一聲線，也不需要跨模型口型同步。

## 三段共用的排除要求

可貼到平台負面提示欄；沒有獨立欄位時，將最重要的幾項加入主提示詞末尾，不使用平台不支援的旗標：

```text
No identity changes, no clothing changes, no extra limbs or fingers, no merged hands, no distorted faces, no unnatural walking, no sudden camera jumps, no scene changes, no invented signs, no text, no subtitles, no logos, no fireworks, no crowds obscuring the subjects. Do not present the scene as documentary footage of a named attraction.
```

## 參數與執行順序

1. 先查當前登入帳戶、模型列表、剩餘額度、音訊選項、每次生成費用與素材使用條件。本次這些狀態未知，不能把三段所需額度填成固定數字。
2. 以平台支援的方式附角色圖或首幀，不自創 `@角色`、seed 或模型 API 欄位。若平台支援 seed，可記錄作輔助，但不把它當人臉鎖定保證。
3. 生成目標設定：每段 10 秒、16:9、目標 1080p；若介面允許，先產無音訊版本。24 fps 是剪輯時間軸目標，生成器輸出不同幀率時再統一，不任意更改播放速度。
4. 先確認 V01 的人物、光影與動態，再依同一標準完成 V02、V03。逐段記錄實際模型、參考圖、提示詞、耗用及輸出尺寸；不在素材不一致時直接拼接。
5. 片段各裁成 240 格，使用 24 fps 組成 720 格。跨段採直接剪接，避免疊化把 30 秒縮短；畫面動作不連續時，先調整剪點或重做片段。
6. 旁白、配樂與環境音後製加入；全片「AI 生成示意畫面」、逐字字幕與 CTA 也由剪輯軟體疊加。

## 配音提示詞與配樂製作簡報

下列是可交給配音者／音樂製作者或相應工具的文字規格，並非已生成素材。

**配音風格提示詞（搭配三段台詞分次錄製）：**

```text
使用台灣華語，由同一位成年女性以溫暖、沉穩、自然的口吻朗讀。清楚咬字，依逗號與句號保留停頓，不使用誇張銷售腔，不模仿特定真人。以提供的台詞逐字朗讀，不加字、不念段名，不加背景音樂。每段需容納於10秒畫面中，錄製後先量測時長再對齊，避免為了壓秒而不自然加速。
```

**配樂氣氛提案：**

```text
Thirty-second instrumental travel underscore, approximately 80 BPM. A gentle piano motif with lightly plucked acoustic guitar, joined by restrained warm strings in the middle. Consistent pulse across all three ten-second scenes, spacious midrange for Mandarin narration, subtle natural dynamics, calm resolving ending. No vocals, no lyrics, no choir, no dramatic impact hits. Compose an original melody without imitating an existing song.
```

配樂方向尚待製作時確認，不能以此提示詞宣稱已有商用授權；使用任何生成或素材音樂前應核對該曲目及平台實際條件。

## 教學與自學檢查

- 先找角色、動作、場景、運鏡、光影五項，再貼入生成器。不要把整份分鏡文件當成單一生成提示詞。
- 場景首幀先驗證，再做動態，可降低重新生成的人物漂移風險，但不能保證完全一致。
- 電影感來自構圖、光質與穩定動作，不是加入未查證的花火、豪華設施或景點保證。
- 檢視最終影片時，逐段對照 [storyboard.md](storyboard.md) 的事實界線、角色表、時間軸與來源。本次僅完成文字素材，未宣稱生成品質、配音秒數或影片驗收通過。
