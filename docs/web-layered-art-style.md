# Web 分圖層畫風規範（草案 v1，2026-10-28）

用途：Web 寵物改用 Livly 式「分圖層動畫」時的共同畫風、拆零件與製作流程。來源是白鳥試作（`web-preview/bird-layered-preview.html`）。逐格動畫的通用規則仍見 [web-sprite-workflow.md](web-sprite-workflow.md)，兩者衝突時以本文件為準；當次艾瑪的指示優先於兩者。

**現況**：只有白鳥做過一次試作，尚未接入正式 Web。艾瑪已確認的部分：試作 A 圖的畫風（2026-10-28「好可愛」），頭與身體的切線位置，以及預覽成品（「比原本的小鳥可愛多了，還很靈動」）。第 6 節的動作數值是初版，尚未逐項確認。小飛龍、貓、蛋與 UI 都還沒開始。韌體像素圖不受影響。

## 1. 畫風

- 平滑的 2D 平塗插畫，接近可愛手機養成遊戲（例如 Livly Island）。**不是**像素畫。
- **完全不描邊**：形狀只靠色塊交界區分。這是分圖層的前提：零件轉動時，交界處同色疊同色，就看不出接縫。
- 每個部位平塗，最多再加一層柔和的陰影或亮面。不畫材質、羽毛紋、毛流或漸層光暈。
- 輪廓圓潤平滑。蓬毛只用兩三撮大而軟的形狀表現，邊緣不做細碎的毛。細碎毛邊很難去背，轉動時也容易露出白邊。
- 五官簡化：眼睛是深色橢圓加一個白色亮點（方便程式畫眨眼和眼皮），腮紅是柔和的粉色橢圓。
- 背景、地面、陰影、文字、道具一律不畫，效果另外做。

## 2. 比例與構圖

- 頭大身圓，頭約佔全身高度的一半以上，四肢短小。
- 視角固定為正面偏四分之三；同一角色所有零件和表情都用同一個視角。
- 可動部位（耳、翅膀、尾巴、腳）要畫成輪廓清楚、互相分開的色塊，盡量不跟其他部位交纏。
- 生成畫布為正方形（1024 或 1254 px），角色置中，四周留空，背景是純綠 `#00FF00`，不要漸層。

## 3. 配色

每個角色有自己的固定色盤，記在各角色的素材說明。白鳥試作的基準色（取自 `layered-test-a-v1.webp`）：

| 部位 | 顏色 |
|---|---|
| 頭、胸口奶油色 | `#fdf8ee` |
| 下身米色 | `#f2e8de` |
| 眼睛／亮點 | `#563628`／`#fefdff` |
| 腮紅 | `#febfbb` |
| 喙、腳、翅膀深灰 | `#57565f` 一帶 |
| 翅膀白邊／淺灰 | `#f3f3f3`／`#e3e2e7` |
| 尾巴中灰 | `#b1afbb` |

同一角色的不同零件與表情不能偏色。改色要從色盤改，不能讓 GPT 每次各自發揮。

## 4. 拆零件規則

### 原則

- **以完整圖 A 為準**：零件優先由 Claude 從艾瑪確認的完整角色圖直接切，這樣尺寸和位置必定對得上。
  白鳥試作中，GPT 一次拆出的零件圖有三個問題：比例不一致（腳偏大、尾巴偏小）、把翅膀畫成第二根尾巴、頭和身體切錯位置。
  所以 GPT 零件圖只用來參考 A 裡被擋住的形狀（例如尾巴完整的樣子），或在 A 擋住太多時才使用。
- **切線放在同色區域內**：頭和身體要切在顏色連續的地方。白鳥的切線在胸口上方（艾瑪手畫），胸口歸身體，所以頭轉動時切口是奶油色疊奶油色，不會露餡。
  不要沿著兩種顏色的交界切，交界一動就會露出來。
  分不清楚的切線由艾瑪畫在 A 上，Claude 換算成座標記在整理工具裡。
- **被擋住的部分要補**：
  - 頭底下的身體：從切線往上至少補 110 px（以 1254 px 畫布計）。
  - 翅膀、尾巴、腳被蓋住的一端：補成圓弧收尾。
  - 補色範圍往外多擴幾個像素，蓋掉反鋸齒留下的細縫。
- **手修檔**：程式補得不夠自然時由艾瑪手修，存成 `<零件>-hand-vN.png`，尺寸和位置不變。整理工具重跑時優先使用手修檔，不會覆蓋。

### 白鳥的零件與疊放順序

由後到前：尾巴 → 左腳、右腳 → 身體（奶油色胸口＋米色下身）→ 翅膀 → 頭（含眼睛、腮紅、喙）。

旋轉支點：
- 頭：脖子，切線中央略上方
- 翅膀：肩部
- 尾巴：根部
- 腳：腳跟上緣
- 身體：底部中央（呼吸時以此為基準縮放）

需要張嘴的角色，嘴或喙之後再拆成獨立零件；目前白鳥的喙留在頭上。

## 5. 製作流程

1. **A：完整角色圖**。艾瑪用第 8 節的範本請 GPT 畫，附上角色現有的基準圖當造型參考，確認畫風和造型。
2. **切零件**。Claude 依顏色從 A 切出零件；顏色分不開的交界，用看得到的邊緣點擬合曲線補上。需要時請艾瑪畫切線。
3. **補被擋住的部分**，再輸出零件 PNG 與定位資料：位置、支點、眼睛橢圓、疊放順序。工具範例：`tools/prepare_bird_layered_test.py`。
4. **組合檢查**。組合圖要和 A 疊圖比對，幾乎重合才算對位正確。
5. **預覽頁檢查**。暫停時間軸，跳到每個動作幅度最大的那一刻放大檢查交界，包括歪頭（左右）、拍翅、甩尾、跳躍、眨眼半閉與全閉。不能只看自動播放的縮小畫面。
6. **交付**。標明已切、已補、已檢查和待艾瑪確認的部分。手修過的零件記在素材說明。

## 6. 動畫規則

- 動作盡量由程式驅動零件，不為「只差一點」的動作請 GPT 重畫整張圖。這正是分圖層的目的：避免逐格生成時整隻抖動。
- 子零件跟著身體走：身體呼吸或壓扁時，頭、翅膀、尾巴的支點依身體縮放一起位移，零件本身不跟著縮放。
- 多個小動作錯開週期疊加，例如呼吸、甩尾、歪頭、眨眼各用不同週期，避免看起來像固定迴圈。
- 減少動態模式：停在靜止姿勢，只保留狀態必要的表情。

白鳥試作的初版數值（尚未逐項確認）：

| 動作 | 數值 |
|---|---|
| 呼吸 | 3.2 秒一次，身體高 ±1.8%、寬 ∓0.6% |
| 甩尾 | ±4°、1.4 秒擺動；每 4.3 秒快速上甩 14° |
| 歪頭 | 微晃 ±1.5°；每 6 秒左右輪流歪 10°，停約 0.9 秒 |
| 眨眼 | 約每 3.7 秒一次，閉 60 ms、停 50 ms、開 70 ms；每三次有一次連眨 |
| 拍翅 | 0.9 秒拍三下，最大 28° |
| 跳躍 | 蹲 160 ms → 騰空 480 ms → 落地壓扁 260 ms；腳比身體晚離地 |
| 踏步 | 每步 520 ms，左右腳輪流抬起 |

## 7. 各狀態的做法

先判斷能不能用程式組出來；只有換姿勢或新表情才需要新圖。新表情只畫頭（同尺寸、同位置、同視角），不重畫全身。

| 狀態 | 程式能做的 | 需要的新圖 |
|---|---|---|
| 待機 | 呼吸、甩尾、歪頭、眨眼 | 無 |
| 開心／摸摸 | 輕跳、甩尾加快 | 笑眼（簡單弧線也可由程式畫） |
| 傷心 | 頭低垂、尾巴下垂、眨眼變慢 | 委屈眼神或含淚的頭 |
| 生病 | 緩慢搖晃、半閉眼（程式畫眼皮） | 視情況補疲倦表情 |
| 嚇一跳 | 跳起、翅膀張開、尾巴翹起 | 睜大眼、張嘴（需另拆喙） |
| 吃飯／喝水 | 低頭啄（頭繞脖子轉）、抬頭吞 | 無；食盆是獨立效果 |
| 散步 | 踏步加整體位移、左右翻面 | 無 |
| 睡眠 | 閉眼、呼吸放慢 | 縮成一團的姿勢可能要整張新圖 |
| 長眠 | 不適用 | 躺倒姿勢的整張單圖，不分圖層 |

各角色要依自己的習性調整，例如小飛龍可以飛、貓有耳朵和長尾巴。不直接套用白鳥的動作。

## 8. 提示詞範本

### 完整角色圖（A）

附圖：該角色已確認的基準圖（只參考角色造型，不參考畫風）。

```
The attached image shows the character: 【角色固定特徵：體型、五官、配色、可動部位】. Redraw this same character, same pose, same facing direction and same colors, but in this art style:

- Soft, smooth, flat 2D illustration like a cute mobile pet game (simple vector-like shapes, the style of games such as Livly Island).
- NO outlines at all: no dark line around any part. Shapes are defined only by color.
- NOT pixel art. Smooth clean edges.
- Flat colors with only one soft, subtle shade on each part. No texture, no individual feathers, no fur strands.
- Smooth round silhouette with at most two or three small soft tufts. No jagged fluffy edges.
- Eyes are simple: a dark oval with one white highlight dot. Blush is a soft pink oval.
- 【each movable part: wing / tail / ears / feet】 is one clear, separate shape, so it could be cut out and moved later.

One character centered with empty space around it. No text, no props, no ground, no shadow. Background: one flat solid pure green (#00FF00) everywhere outside the character, no gradient.
```

### 表情頭（只換五官）

附圖：已確認的 A 圖。

```
The attached image is the finished character. Draw ONLY its HEAD, exactly the same size, shape, angle, colors and art style (no outlines, flat colors), with only this change: 【表情：例如 eyes closed in gentle downward curves, a small tear at the corner of each eye】. Everything else on the head stays exactly the same: tufts, blush, beak and outline shape. Cut the bottom of the head along the same line as the original head piece. Background: one flat solid pure green (#00FF00), no text, no props.
```

簡單的表情（閉眼線、半閉眼皮、笑眼弧線）優先由程式畫，不必生成。

## 9. 驗收清單

- 零件組合圖和 A 疊圖幾乎重合；沒有綠邊、白邊、細縫或破洞。
- 每個動作的最大幅度都放大檢查過交界，沒有露出切口、空隙或錯誤的疊放順序。
- 眨眼的半閉與全閉都自然，眼皮顏色和頭部一致。
- 減少動態時角色靜止，而且姿勢完整。
- 在實際背景上看過大小和畫風是否協調。目前的像素風花園與新畫風不搭，背景屬於 UI 改版範圍。
- 艾瑪確認前，不把預覽說成已驗收。

## 10. 待決定

- 第 6 節的動作數值。
- 換全寵物的順序：建議白鳥完整換掉 → 小飛龍 → 貓 → 蛋與孵化 → UI。
- 新舊美術並存期間的切換方式：建議先做新版的狀態用新圖，其餘沿用舊圖。
- 正式素材的目錄。建議 `web-preview/assets/pets/<物種>/<階段>/layered-v1/`，內含 A 圖、手修檔、零件與定位資料；試作目錄 `bird/layered-test/` 保留作紀錄。
- UI（按鈕、面板、背景）配合新畫風的改版範圍。
