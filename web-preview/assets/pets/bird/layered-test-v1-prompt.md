# 白鳥分圖層動畫試作 v1 提示詞（2026-10-28 草稿）

目的：測試 Livly 式「分圖層動畫」——無描邊、平塗的畫風，把身體、翅膀、尾巴分開畫，
由程式旋轉／位移零件做甩尾、拍翅、呼吸，眨眼由程式在臉上畫眼皮。這只是試作，不取代現行白鳥素材。

分兩步：先畫新畫風的完整白鳥（A），艾瑪看過覺得可以，再拿 A 去拆零件（B）。

## A：新畫風的完整白鳥

附圖：`white-idle-v2.png`（白鳥基準，只參考角色，不參考畫風）。

輸出：1024×1024 正方形，單一角色。

```
The attached image shows the character: a round white bird (like a long-tailed tit) with big brown eyes, pink blush cheeks, a tiny dark beak, dark grey-black folded wings, a long black-and-white tail and small dark feet. Redraw this same character, same pose, same facing direction and same colors, but in a completely different art style:

Style:
- Soft, smooth, flat 2D illustration like a cute mobile pet game (simple vector-like shapes, the style of games such as Livly Island).
- NO outlines at all: no dark line around the body, wings, tail or feet. Shapes are defined only by color.
- NOT pixel art. Smooth clean edges.
- Flat colors with only one soft, subtle shade on each part (a slightly darker cream-white on the lower belly, a slightly lighter grey on the wing edge). No texture, no individual feathers, no fur strands.
- The body silhouette is a smooth round shape with at most two or three small soft feather tufts on top of the head. No jagged fluffy edges.
- Eyes are simple: a dark brown oval with one white highlight dot. Blush is a soft pink oval.
- The wing and the tail are each one clear, separate shape, so they could be cut out and moved later.

One character centered with empty space around it. No text, no props, no ground, no shadow. Background: one flat solid pure green (#00FF00) everywhere outside the character, no gradient.
```

### 若結果不理想的追加指示

- 還是有描邊：`Remove every outline. There must be no dark line along any edge; edges are just where one color meets another.`
- 邊緣毛茸茸：`Make the body edge smooth and round like a soft ball; only two or three tufts on the top of the head.`
- 太寫實、羽毛太多：`Simplify into a few big flat shapes, like a sticker, without feather details.`

## B：拆成零件圖

附圖：A 的成品 `layered-test-a-v1.webp`（艾瑪 2026-10-28 確認）。

A 的頭本來就是疊在下身上的一顆圓，拆開後可以做歪頭、點頭、啄食；腳拆開可以做走路抬腳、
跳躍時腳先離地。所以拆五塊：頭、下身、翅膀、尾巴、左右腳。
眼睛、腮紅、喙留在頭上：眨眼由程式畫，張嘴（嚇一跳、吃飯）之後需要再另外拆喙。

輸出：1536×1024 橫向（若只能正方形就用 1024×1024）。

```
The attached image is the finished character. Make a character parts sheet for cut-out animation, in exactly the same art style, colors and scale as the attached image (no outlines, flat colors, smooth edges).

Draw these pieces separately, spread out with wide empty space between every piece, all at exactly the same size as in the attached image:
1. HEAD: the round cream head with the feather tufts, both eyes, both blush cheeks and the beak. Its bottom edge is a complete smooth round curve (the part normally hidden behind nothing is just finished as the round head shape).
2. BODY: only the lower beige body, WITHOUT the head, wing, tail and feet. Its top is a complete smooth round shape where the head used to sit, and the area where the wing used to cover it is painted as plain body color, so nothing looks missing.
3. WING: only the dark folded wing with its white edge feathers, as one separate shape, same angle as on the character.
4. TAIL: only the long black, white and grey tail, as one separate shape, same angle as on the character. Its base end (where it joins the body) is slightly rounded.
5. LEFT FOOT and 6. RIGHT FOOT: each small dark foot alone, same shape and angle as on the character, with a short rounded top where it joins the body.

Do not change the shape, size or colors of any piece compared with the attached image. No text, no labels, no numbers, no arrows, no props. Background: one flat solid pure green (#00FF00) everywhere outside the pieces, no gradient.
```

### 若結果不理想的追加指示

- 身體上還留著翅膀或頭：`The BODY piece must have no head and no wing at all; finish its top as a smooth round body shape.`
- 頭底部被切平：`The HEAD piece must be a complete round head; its bottom is a smooth curve, not a flat cut.`
- 零件大小跟原圖不一樣：`Each piece must be exactly the same size as on the attached character, so they fit back together.`
- 零件擠在一起或互相碰到：`Leave wide empty green space between all pieces; no piece may touch another.`

### B 第一次結果（`layered-test-b-v1.webp`）

- 頭、左右腳可用；頭底部有補成完整圓形。
- 翅膀失敗：畫了兩根一樣的尾巴，沒有 A 裡的深灰翅膀。
- 下身頂部畫成往下凹的弧（只畫出原本露出來的部分），兩側肩角是尖的，歪頭時會露出來。
  下身是平塗單色，由 Claude 用程式把頂部補成圓頂，不重生。

## C：單獨重拆翅膀

GPT 一次拆多個零件時容易把翅膀和尾巴搞混，所以翅膀單獨一張。

附圖：`layered-test-a-v1.webp`。

輸出：1024×1024 正方形。

```
The attached image is the finished character. Draw ONLY its WING as a single separate piece for cut-out animation, in exactly the same art style, colors, scale and angle as in the attached image (no outlines, flat colors, smooth edges).

Which piece is the wing: the dark charcoal-grey folded wing lying on the right side of the body, just below the right pink cheek. It is a curved dark shape that starts under the head and sweeps down to a point at the lower right, with a scalloped white and light-grey feather edge along its lower part.
It is NOT the tail. The tail is the long striped feathers sticking up behind the bird; do not draw the tail at all.

The top end of the wing, which is hidden under the head in the attached image, is finished as a smooth rounded end. Draw nothing else: no body, no head, no tail, no feet.

One piece centered with empty space around it. No text, no labels, no props. Background: one flat solid pure green (#00FF00) everywhere outside the piece, no gradient.
```

### 若結果不理想的追加指示

- 又畫成尾巴：`This is wrong, that is the tail. Draw the short dark folded wing that lies against the body below the right cheek, with the scalloped white edge.`
- 翅膀太大或角度不同：`Keep the wing exactly the size and angle it has on the attached character.`

## 接入時

收到 B 後由 Claude 整理：去綠底、切出各零件、以 A 為參考比對出各零件位置與旋轉支點
（頸部、尾巴根部、翅膀肩部、腳跟），輸出零件 PNG 與定位資料，再做獨立預覽頁：
尾巴擺動、翅膀微拍、身體呼吸起伏、歪頭、程式眨眼，以及走路抬腳。
疊放順序（後到前）：尾巴、腳、下身、翅膀、頭。先只做預覽，不接入正式 Web。

## 試作結果（2026-10-28）

實際做法與提示詞原本的規劃不同：B 圖只採用尾巴和腳；頭、身體、翅膀由 Claude 從 A 圖切出，頭依艾瑪畫的線切在胸口上方。
身體頂部和翅膀上端由艾瑪手修（`layered-test-body-hand-v1.png`、`layered-test-wing-hand-v1.png`）。
預覽頁 `web-preview/bird-layered-preview.html`；整理工具 `tools/prepare_bird_layered_test.py`。
從這次整理出的共同規範見 `docs/web-layered-art-style.md`。
