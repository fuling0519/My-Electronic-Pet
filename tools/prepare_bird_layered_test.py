"""Turn the white-bird cut-out test art into layered parts for the animation preview.

Usage: python tools/prepare_bird_layered_test.py
Input (web-preview/assets/pets/bird/):
  layered-test-a-v1.webp     the assembled bird, 1254 px square (the layout reference)
  layered-test-b-v1.webp     ChatGPT parts sheet: head, body, two tails, two feet
                             (only the tail and feet are used)
  layered-test-wing-v1.png   the wing, cut out of image A (its bbox in A is WING_BOX)
  layered-test-<part>-hand-v1.png  艾瑪's hand-painted fixes (rounded body top, rounded
                             wing top); when present they replace the generated part,
                             and must keep its size and place
Output (web-preview/assets/pets/bird/layered-test/): head/body/tail/foot-left/foot-right/wing.png
  and layout-v1.js / layout-v1.json with each part's place in A's 1254 px canvas,
  rotation pivots and the eye ellipses used to draw blinks.

The head and body are cut straight out of A along HEAD_CUT: the head keeps the face,
the body is the cream chest plus the beige belly. Where the head and wing cover the
body, it is refilled inside an ellipse fitted to its visible outline, cream above the
chest line and beige below. The sheet's own head and body were not used: its head
included the chest and its body top was cut concave, so they looked wrong together.
The sheet's tail and feet are not in proportion with A, so each gets the scale and
position that best covers its region in A without spilling onto A's background.
Needs numpy.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

DIR = Path(__file__).resolve().parent.parent / "web-preview" / "assets" / "pets" / "bird"
OUT = DIR / "layered-test"
WING_BOX = (706, 641)  # top-left of layered-test-wing-v1.png inside image A
# Where the head ends and the cream chest begins, traced by hand on image A and scaled to
# its 1254 px canvas. The chest belongs to the body, so the head's cut edge is cream over
# cream and never shows when the head tilts.
HEAD_CUT = [(100, 560), (158, 605), (193, 632), (227, 663), (262, 687), (297, 708), (331, 722),
            (366, 736), (401, 746), (436, 757), (470, 770), (505, 779), (540, 786), (574, 791),
            (609, 794), (644, 794), (678, 794), (713, 792), (800, 790)]
HEAD_PIVOT = [440, 745]  # neck, just above the middle of the cut


def load(name):
    return np.asarray(Image.open(DIR / name).convert("RGB")).astype(int)


def green(img):
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    return (g > 170) & (g - np.maximum(r, b) > 60)


def components(mask, min_size):
    """4-connected components as (mask, bbox) pairs, largest first."""
    h, w = mask.shape
    seen = np.zeros_like(mask)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        stack, pts = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(pts) >= min_size:
            ys, xs = np.array(pts).T
            m = np.zeros_like(mask)
            m[ys, xs] = True
            out.append((m, (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)))
    return sorted(out, key=lambda c: -c[0].sum())


def fill_holes(mask):
    """Fill enclosed holes (eyes, blush and beak inside the head)."""
    outside = components(~mask, 1)
    keep = np.zeros_like(mask)
    h, w = mask.shape
    for m, (x0, y0, x1, y1) in outside:
        if x0 == 0 or y0 == 0 or x1 == w or y1 == h:
            keep |= m
    return ~keep


def rgba_part(img, mask, box):
    x0, y0, x1, y1 = box
    sub = img[y0:y1, x0:x1].copy()
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    sub[..., 1] = np.minimum(g, np.maximum(r, b) + 4)  # despill the green fringe
    a = mask[y0:y1, x0:x1].astype(np.uint8) * 255
    return np.dstack([sub, a]).astype(np.uint8)


def resize(part, s):
    im = Image.fromarray(part, "RGBA")
    w, h = im.size
    return np.asarray(im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS))


def corr(big, small):
    """score[y, x] = sum(big[y:y+h, x:x+w] * small), via FFT."""
    H, W = big.shape
    h, w = small.shape
    fh, fw = H + h, W + w
    f = np.fft.irfft2(np.fft.rfft2(big, (fh, fw)) * np.conj(np.fft.rfft2(small, (fh, fw))), (fh, fw))
    return f[:H - h + 1, :W - w + 1]


def place(mask, target, background, scales, step=2):
    """Best (score, scale, x, y) putting a part mask over its region in A, at A/step resolution."""
    t = target[::step, ::step].astype(float)
    bg = background[::step, ::step].astype(float)
    best = None
    for s in scales:
        m = resize(np.dstack([np.zeros(mask.shape + (3,), np.uint8), mask.astype(np.uint8) * 255]), s / step)
        m = (m[..., 3] > 127).astype(float)
        score = corr(t, m) - 3 * corr(bg, m)
        y, x = np.unravel_index(np.argmax(score), score.shape)
        if best is None or score[y, x] > best[0]:
            best = (score[y, x], s, x * step, y * step)
    return best


def eyes(part):
    """Dark-brown eye ellipses (cx, cy, rx, ry, angle) in the head part's pixels."""
    r, g, b, a = (part[..., i].astype(int) for i in range(4))
    brown = (a > 0) & (r < 120) & (r > 60) & (g < 80) & (b < 70)
    out = []
    for m, _ in components(brown, 200)[:2]:
        ys, xs = np.nonzero(m)
        cx, cy = xs.mean(), ys.mean()
        cov = np.cov(np.vstack([xs - cx, ys - cy]))
        vals, vecs = np.linalg.eigh(cov)
        ang = float(np.arctan2(vecs[1, 1], vecs[0, 1]))
        out.append([round(cx, 1), round(cy, 1), round(2 * np.sqrt(vals[1]), 1),
                    round(2 * np.sqrt(vals[0]), 1), round(ang, 3)])
    return sorted(out)


def below(shape, line):
    """True under the polyline (x ascending), extended flat past both ends."""
    h, w = shape
    xs, ys = np.array(line, float).T
    edge = np.interp(np.arange(w), xs, ys)
    return np.arange(h)[:, None] > edge[None, :]


def fit_ellipse(mask, outside):
    """Axis-aligned ellipse fitted to the mask's border with `outside` (cx, cy, rx, ry)."""
    border = mask & (np.roll(outside, 1, 0) | np.roll(outside, -1, 0)
                     | np.roll(outside, 1, 1) | np.roll(outside, -1, 1))
    ys, xs = np.nonzero(border)
    # a x^2 + b y^2 + c x + d y = 1
    M = np.column_stack([xs ** 2, ys ** 2, xs, ys]).astype(float)
    a, b, c, d = np.linalg.lstsq(M, np.ones(len(xs)), rcond=None)[0]
    cx, cy = -c / (2 * a), -d / (2 * b)
    k = 1 + a * cx ** 2 + b * cy ** 2
    return cx, cy, np.sqrt(k / a), np.sqrt(k / b)


def grow(mask, n):
    for _ in range(n):
        mask = mask | np.roll(mask, 1, 0) | np.roll(mask, -1, 0) | np.roll(mask, 1, 1) | np.roll(mask, -1, 1)
    return mask


def body_from_a(A, cream, head, wing, bg, cut, band=110):
    """The two-tone body (cream chest, beige belly), refilled where the head and wing cover it.

    Under the head it is filled `band` px up from the cut line, so a tilting head never
    uncovers a gap; under the wing, inside an ellipse fitted to the body's visible outline.
    Both grow 4 px so the anti-aliased seam pixels between the parts are filled too.
    """
    g = A[..., 1]
    beige = ~bg & (g < 240) & (g > 222)
    vis = [c for c in components((cream & ~head) | (beige & ~wing), 5000) if c[0][900, 300]][0][0]
    cx, cy, rx, ry = fit_ellipse(vis, bg)
    h, w = vis.shape
    yy, xx = np.mgrid[0:h, 0:w]
    inside = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    xs, ys = np.array(cut, float).T
    edge = np.interp(np.arange(w), xs, ys)[None, :]
    fill = ~bg & ~vis & ((grow(head, 4) & (yy > edge - band)) | (grow(wing, 4) & inside))
    # Where the cream chest turns beige, per column; extended under the wing with a fitted curve.
    cols, rows = [], []
    for x in range(w):
        b = np.nonzero(vis[:, x] & beige[:, x])[0]
        c = np.nonzero(vis[:, x] & cream[:, x])[0]
        if len(b) and len(c) and b[0] > c[0] and not wing[:, x].any():
            cols.append(x)
            rows.append(b[0])
    split = np.polyval(np.polyfit(cols, rows, 2), np.arange(w))
    # Pixels between cream and beige fit neither colour; keep them from A as holes in the body.
    vis = fill_holes(vis | fill) & ~fill
    out = np.zeros((h, w, 4), np.uint8)
    out[vis, :3] = A[vis]
    out[vis, 3] = 255
    for colour_mask, cond in ((cream & vis, yy < split[None, :]), (beige & vis, yy >= split[None, :])):
        colour = np.median(A[colour_mask], axis=0).astype(np.uint8)
        out[fill & cond, :3] = colour
        out[fill & cond, 3] = 255
    return out


def main():
    A, B = load("layered-test-a-v1.webp"), load("layered-test-b-v1.webp")
    wing = np.asarray(Image.open(DIR / "layered-test-wing-v1.png").convert("RGBA"))

    # --- tail and feet from sheet B, picked by where ChatGPT put them ---
    comps = components(~green(B), 2000)
    def pick(fx, fy):
        h, w = B.shape[:2]
        return min(comps, key=lambda c: (((c[1][0] + c[1][2]) / 2 - fx * w) ** 2
                                         + ((c[1][1] + c[1][3]) / 2 - fy * h) ** 2))
    sheet = {"head": pick(0.19, 0.3), "tail": pick(0.86, 0.38),
             "foot-left": pick(0.5, 0.84), "foot-right": pick(0.79, 0.84)}
    parts = {k: rgba_part(B, m, box) for k, (m, box) in sheet.items()}

    # --- head and body cut straight out of image A ---
    bgA = green(A)
    g = A[..., 1]
    wing_full = np.zeros(bgA.shape, bool)
    wy, wx = WING_BOX[1], WING_BOX[0]
    wing_full[wy:wy + wing.shape[0], wx:wx + wing.shape[1]] = wing[..., 3] > 0
    cream = [c for c in components(~bgA & (g >= 242) & ~wing_full, 5000) if c[0][300, 500]][0][0]
    under = below(bgA.shape, HEAD_CUT)
    head_c = [c for c in components(cream & ~under, 5000) if c[0][300, 500]][0][0]
    headA = fill_holes(head_c)
    body = body_from_a(A, cream & under, headA, wing_full, bgA, HEAD_CUT)
    bodyA = body[..., 3] > 0
    OUT.mkdir(exist_ok=True)
    layout = {"canvas": 1254, "parts": {}}
    for name, mask, rgba in (("head", headA, None), ("body", bodyA, body)):
        ys, xs = np.nonzero(mask)
        box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        img = rgba_part(A, mask, box) if rgba is None else rgba[box[1]:box[3], box[0]:box[2]]
        Image.fromarray(img, "RGBA").save(OUT / f"{name}.png")
        layout["parts"][name] = {"x": int(box[0]), "y": int(box[1]), "w": img.shape[1], "h": img.shape[0]}

    # --- where the sheet's tail and feet sit in image A ---
    yy, xx = np.mgrid[0:A.shape[0], 0:A.shape[1]]
    tailA = ~bgA & ~fill_holes(cream) & ~bodyA & ~wing_full & (xx > 900) & (yy < 1010)
    feetA = ~bgA & ~bodyA & (yy > 1060) & (A[..., 0] < 140)
    targets = {"tail": tailA, "foot-left": feetA & (xx < 480), "foot-right": feetA & (xx >= 480)}

    # ChatGPT did not keep the sheet's parts in proportion (the feet came out larger), so
    # each part gets its own scale, searched around the sheet head's scale to A's cream head.
    s0 = fill_holes(cream).any(axis=0).sum() / (parts.pop("head")[..., 3] > 0).any(axis=0).sum()
    for name, part in parts.items():
        _, s, x, y = place(part[..., 3] > 0, targets[name], bgA,
                           np.linspace(s0 * 0.65, s0 * 1.35, 29))
        small = resize(part, s)
        Image.fromarray(small, "RGBA").save(OUT / f"{name}.png")
        layout["parts"][name] = {"x": int(x), "y": int(y), "w": small.shape[1], "h": small.shape[0],
                                 "scale": round(float(s), 4)}
    Image.fromarray(wing, "RGBA").save(OUT / "wing.png")
    layout["parts"]["wing"] = {"x": WING_BOX[0], "y": WING_BOX[1], "w": wing.shape[1], "h": wing.shape[0]}

    for name, info in layout["parts"].items():
        hand = DIR / f"layered-test-{name}-hand-v1.png"
        if hand.exists():
            im = Image.open(hand).convert("RGBA")
            assert im.size == (info["w"], info["h"]), f"{hand.name} must stay {info['w']}x{info['h']}"
            im.save(OUT / f"{name}.png")
            info["hand"] = hand.name

    # Pivots, in A canvas pixels.
    P = layout["parts"]
    def lowest(name, frac):
        """Centre of the part's lowest `frac` of rows, placed in A."""
        a = np.asarray(Image.open(OUT / f"{name}.png"))[..., 3] > 0
        rows = np.nonzero(a.any(axis=1))[0]
        cut = rows[-1] - (rows[-1] - rows[0]) * frac
        ys, xs = np.nonzero(a & (np.arange(a.shape[0])[:, None] >= cut))
        return [round(P[name]["x"] + xs.mean()), round(P[name]["y"] + ys.mean())]
    body = P["body"]
    layout["pivots"] = {
        "head": HEAD_PIVOT,
        "tail": lowest("tail", 0.08),
        "wing": [WING_BOX[0] + 40, WING_BOX[1] + 70],
        "body": [body["x"] + body["w"] // 2, body["y"] + body["h"]],
        "foot-left": [P["foot-left"]["x"] + P["foot-left"]["w"] // 2, P["foot-left"]["y"]],
        "foot-right": [P["foot-right"]["x"] + P["foot-right"]["w"] // 2, P["foot-right"]["y"]],
    }
    headpart = np.asarray(Image.open(OUT / "head.png"))
    layout["eyes"] = eyes(headpart)  # in head.png pixels
    layout["headColour"] = "#%02x%02x%02x" % tuple(int(v) for v in np.median(
        headpart[headpart[..., 1] >= 242][:, :3], axis=0))
    layout["order"] = ["tail", "foot-left", "foot-right", "body", "wing", "head"]

    text = json.dumps(layout, ensure_ascii=False, indent=1)
    (OUT / "layout-v1.json").write_text(text + "\n", encoding="utf-8")
    (OUT / "layout-v1.js").write_text(f"window.BIRD_LAYERED_LAYOUT={text};\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
