# -*- coding: utf-8 -*-
"""Claude Homebase graphic: an isometric voxel island (Minecraft style) with one building per level.

role (CLAUDE.md) -> tasks (skills/) -> projects (projects/<name>/) -> knowledge (learnings/) -> tools (tools/)

Outputs (next to this script):
  homebase.png        1280x640, README header and GitHub social preview
  homebase-build.gif  960x480, the base built block by block

Needs Pillow only:  pip install pillow
Fonts: Montserrat and Aptos from HOMEBASE_FONT_DIR (falls back to the Pillow default font).
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get("HOMEBASE_FONT_DIR", r"C:\Users\anton\OneDrive\Mabya\Dokumente\Claude\fonts")

W, H = 1280, 640                     # design canvas
BG = (12, 17, 21)                    # #0c1115
ORANGE = (246, 87, 30)               # #f6571e
ORANGE2 = (255, 145, 44)             # #ff912c
WHITE = (255, 255, 255)
GREY = (201, 205, 210)               # #c9cdd2
GREY2 = (139, 144, 150)              # #8b9096
CARD = (19, 24, 30)                  # #13181e

# island geometry (grid units) and screen placement (design px)
R = 10.5                              # plateau radius (superellipse)
U = 18                                # half tile width in px at scale 1
CX, CY = 862, 326                     # screen position of grid origin


# ------------------------------------------------------------------ materials
def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


MAT = {
    "grass":  dict(top=hx("#3fae63"), side=hx("#7a5230"), jitter=0.07, kind="grass"),
    "dirt":   dict(top=hx("#7a5230"), side=hx("#7a5230"), jitter=0.08),
    "stone":  dict(top=hx("#8b9096"), side=hx("#8b9096"), jitter=0.09),
    "cobble": dict(top=hx("#6a7076"), side=hx("#6a7076"), jitter=0.12),
    "plank":  dict(top=hx("#c99a57"), side=hx("#c99a57"), jitter=0.04, kind="plank"),
    "dark":   dict(top=hx("#5a3b1c"), side=hx("#5a3b1c"), jitter=0.04, kind="plank"),
    "roof":   dict(top=ORANGE, side=ORANGE, jitter=0.03),
    "roof2":  dict(top=ORANGE2, side=ORANGE2, jitter=0.03),
    "glass":  dict(top=hx("#39a3d1"), side=hx("#39a3d1"), jitter=0.02, kind="glass"),
    "door":   dict(top=hx("#2b1d10"), side=hx("#2b1d10"), jitter=0.02),
    "navy":   dict(top=hx("#043959"), side=hx("#043959"), jitter=0.04),
    "blue":   dict(top=hx("#2f8ae5"), side=hx("#2f8ae5"), jitter=0.04),
    "lblue":  dict(top=hx("#39a3d1"), side=hx("#39a3d1"), jitter=0.04),
    "teal":   dict(top=hx("#1abc9c"), side=hx("#1abc9c"), jitter=0.04),
    "lamp":   dict(top=hx("#ffd27a"), side=hx("#ffb347"), jitter=0.02),
    "leaf":   dict(top=hx("#2f9c5f"), side=hx("#2f9c5f"), jitter=0.10),
    "log":    dict(top=hx("#8a6a3e"), side=hx("#5c3d1e"), jitter=0.05, kind="plank"),
    "white":  dict(top=hx("#e9ecef"), side=hx("#e9ecef"), jitter=0.03),
}

SHADE = dict(top=1.0, left=0.84, right=0.66)   # +z, +y, +x faces


def shade(c, f):
    return tuple(max(0, min(255, int(round(v * f)))) for v in c)


def jit(key, amp):
    """Deterministic jitter in [-amp, amp] from a hashable key."""
    h = hashlib.md5(repr(key).encode()).digest()
    return (h[0] / 255.0 * 2 - 1) * amp


# ------------------------------------------------------------------ scene
class Scene:
    def __init__(self):
        self.blocks = {}   # (x,y,z) -> (material, stage)

    def put(self, x, y, z, mat, stage):
        self.blocks[(x, y, z)] = (mat, stage)

    def box(self, x0, x1, y0, y1, z0, z1, mat, stage):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    self.put(x, y, z, mat, stage)

    def visible(self, keys=None):
        """Painter order, hidden blocks removed (all three visible faces covered).
        keys: optional set of (x, y, z) to restrict the scene to (used for the build animation)."""
        blocks = self.blocks if keys is None else {k: v for k, v in self.blocks.items() if k in keys}
        out = []
        for (x, y, z), (mat, stage) in blocks.items():
            if (x + 1, y, z) in blocks and (x, y + 1, z) in blocks and (x, y, z + 1) in blocks:
                continue
            out.append((x, y, z, mat, stage))
        out.sort(key=lambda b: (b[0] + b[1], b[2]))
        return out


def on_island(x, y, r=R, n=3.0):
    return (abs(x + 0.5) / r) ** n + (abs(y + 0.5) / r) ** n <= 1.0


def build_scene():
    s = Scene()
    # ---- stage 0: floating island (grass top at z=0, tapered layers below)
    for z, r in ((0, R), (-1, R - 0.7), (-2, R - 1.8), (-3, R - 3.4), (-4, R - 5.4), (-5, R - 7.6)):
        mat = "grass" if z == 0 else ("dirt" if z == -1 else "stone")
        rr = int(math.ceil(r)) + 1
        for x in range(-rr, rr + 1):
            for y in range(-rr, rr + 1):
                if on_island(x, y, r):
                    s.put(x, y, z, mat, 0)

    # ---- paths (cobble replaces the grass top)
    def path(cells):
        for x, y in cells:
            if (x, y, 0) in s.blocks:
                s.put(x, y, 0, "cobble", 0)

    path([(x, y) for x in range(-4, 2) for y in range(0, 4)])                  # plaza in front of the house
    path([(x, 0) for x in range(-9, -4)])                                      # to learnings (left back)
    path([(-2, y) for y in range(4, 9)])                                       # to skills (left front)
    path([(2, y) for y in range(-4, 0)] + [(x, -4) for x in range(3, 10)])     # street along the projects
    path([(x, 3) for x in range(2, 5)] + [(4, y) for y in range(4, 7)] + [(x, 6) for x in range(5, 8)])  # to tools

    # ---- stage 1: CLAUDE.md house (role), 5x5 planks, orange stepped roof, beacon on top
    x0, x1, y0, y1 = -5, -1, -5, -1
    s.box(x0, x1, y0, y1, 1, 3, "plank", 1)
    s.box(x0 - 1, x1 + 1, y0 - 1, y1 + 1, 4, 4, "roof", 1)
    s.box(x0, x1, y0, y1, 5, 5, "roof", 1)
    s.box(x0 + 1, x1 - 1, y0 + 1, y1 - 1, 6, 6, "roof", 1)
    s.put(-3, -3, 7, "roof2", 1)
    s.put(-3, -3, 8, "lamp", 1)
    for y in (y0 + 1, y1 - 1):                      # windows on the right face (+x)
        s.put(x1, y, 2, "glass", 1)
    s.put(x0 + 3, y1, 2, "glass", 1)                # window on the left face (+y)
    s.put(x0 + 1, y1, 1, "door", 1)                 # door on the left face (+y), two blocks tall
    s.put(x0 + 1, y1, 2, "door", 1)
    s.put(x1, y0 + 2, 1, "door", 1)                 # side door on the right face

    # ---- stage 2: skills/ workshop (tasks), stone walls, stepped teal roof, chimney, one crate per skill
    s.box(-6, -3, 6, 9, 1, 3, "stone", 2)
    s.box(-7, -2, 5, 10, 4, 4, "teal", 2)
    s.box(-6, -3, 6, 9, 5, 5, "teal", 2)
    s.box(-5, -4, 7, 8, 6, 6, "teal", 2)
    s.put(-6, 6, 6, "stone", 2)
    s.put(-6, 6, 7, "stone", 2)
    s.put(-3, 8, 1, "door", 2)
    s.put(-3, 8, 2, "door", 2)
    s.put(-3, 6, 2, "glass", 2)
    s.put(-5, 9, 2, "glass", 2)
    s.put(-1, 8, 1, "blue", 2)
    s.put(-1, 9, 1, "lblue", 2)
    s.put(-1, 8, 2, "roof2", 2)

    # ---- stage 3: projects/ district, three small houses in a row, one roof colour each
    for px, roof in ((2, "blue"), (5, "navy"), (8, "lblue")):
        py = -6
        s.box(px, px + 1, py, py + 1, 1, 2, "plank", 3)
        s.box(px, px + 1, py, py + 1, 3, 3, roof, 3)
        s.put(px, py, 4, "white", 3)                # flag
        s.put(px, py + 1, 1, "door", 3)
        s.put(px + 1, py + 1, 2, "glass", 3)
        s.put(px + 1, py, 2, "glass", 3)

    # ---- stage 4: learnings/ library (knowledge), a tower of stacked book rows with a lamp
    bx0, bx1, by0, by1 = -10, -8, -2, 0
    s.box(bx0, bx1, by0, by1, 1, 1, "stone", 4)
    for z, m in enumerate(("navy", "blue", "teal", "lblue"), start=2):
        s.box(bx0, bx1, by0, by1, z, z, m, 4)
    s.put(bx0 + 1, by0 + 1, 6, "lamp", 4)

    # ---- stage 5: tools/ shed, dark plank walls, stepped stone roof, open front, crafting table, lantern post
    s.box(6, 8, 3, 5, 1, 3, "dark", 5)
    s.blocks.pop((7, 5, 1), None)    # opening on the front-left face (+y)
    s.blocks.pop((7, 5, 2), None)
    s.box(5, 9, 2, 6, 4, 4, "stone", 5)
    s.box(6, 8, 3, 5, 5, 5, "stone", 5)
    s.put(7, 4, 6, "stone", 5)
    s.put(9, 6, 1, "plank", 5)       # crafting table under the eave
    s.put(5, 7, 1, "log", 5)         # lantern post
    s.put(5, 7, 2, "log", 5)
    s.put(5, 7, 3, "lamp", 5)

    # ---- stage 6: trees and a few stones
    def tree(tx, ty, h=3):
        for z in range(1, h + 1):
            s.put(tx, ty, z, "log", 6)
        s.box(tx - 1, tx + 1, ty - 1, ty + 1, h, h + 1, "leaf", 6)
        s.put(tx, ty, h + 2, "leaf", 6)
        for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
            s.blocks.pop((tx + dx, ty + dy, h + 1), None)

    for tx, ty, h in ((-8, -6, 2), (-10, 3, 3), (1, 9, 3), (8, 8, 3)):
        tree(tx, ty, h)
    for sx, sy in ((10, 0), (-7, -8), (3, 9), (-9, 6)):
        if (sx, sy, 0) in s.blocks and (sx, sy, 1) not in s.blocks:
            s.put(sx, sy, 1, "stone", 6)
    return s


# ------------------------------------------------------------------ rendering
def P(x, y, z, S):
    return ((CX + (x - y) * U) * S, (CY + (x + y) * U / 2 - z * U) * S)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def draw_face(draw, corners, color, key, mat, face, n=4):
    """corners: 4 screen points (top-left, top-right, bottom-right, bottom-left) in face space."""
    a, b, c, d = corners
    kind = mat.get("kind")
    for i in range(n):          # rows (0 = top edge of the face)
        for j in range(n):      # columns
            t0, t1 = i / n, (i + 1) / n
            u0, u1 = j / n, (j + 1) / n
            p0 = lerp(lerp(a, b, u0), lerp(d, c, u0), t0)
            p1 = lerp(lerp(a, b, u1), lerp(d, c, u1), t0)
            p2 = lerp(lerp(a, b, u1), lerp(d, c, u1), t1)
            p3 = lerp(lerp(a, b, u0), lerp(d, c, u0), t1)
            col = color
            if kind == "grass" and face != "top":
                col = shade(MAT["grass"]["top"], SHADE[face]) if i == 0 else color
            if kind == "plank" and face != "top" and i % 2 == 1:
                col = shade(col, 0.9)
            if kind == "glass" and (i + j) % n in (0, 1):
                col = shade(col, 1.18)
            f = 1.0 + jit((key, face, i, j), mat["jitter"])
            draw.polygon([p0, p1, p2, p3], fill=shade(col, f))


def draw_block(draw, x, y, z, mat, S):
    m = MAT[mat]
    top = [P(x, y, z + 1, S), P(x + 1, y, z + 1, S), P(x + 1, y + 1, z + 1, S), P(x, y + 1, z + 1, S)]
    right = [P(x + 1, y, z + 1, S), P(x + 1, y + 1, z + 1, S), P(x + 1, y + 1, z, S), P(x + 1, y, z, S)]
    left = [P(x, y + 1, z + 1, S), P(x + 1, y + 1, z + 1, S), P(x + 1, y + 1, z, S), P(x, y + 1, z, S)]
    key = (x, y, z)
    draw_face(draw, top, shade(m["top"], SHADE["top"]), key, m, "top")
    draw_face(draw, left, shade(m["side"], SHADE["left"]), key, m, "left")
    draw_face(draw, right, shade(m["side"], SHADE["right"]), key, m, "right")
    # thin dark edge on the outer silhouette keeps the pixel look crisp
    o = shade(m["side"], 0.45)
    draw.line([top[0], top[1], right[3], right[2], left[3], top[0]], fill=o, width=max(1, int(S * 0.6)))


def font(name, size, S):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, int(size * S))
    except OSError:
        return ImageFont.load_default(int(size * S))


def background(S):
    img = Image.new("RGB", (int(W * S), int(H * S)), BG)
    d = ImageDraw.Draw(img)
    step = 28 * S
    yy = 0
    while yy < H * S:
        xx = 0
        while xx < W * S:
            d.ellipse([xx - 0.6 * S, yy - 0.6 * S, xx + 0.6 * S, yy + 0.6 * S], fill=(24, 30, 36))
            xx += step
        yy += step
    glow = Image.new("RGB", img.size, BG)
    gd = ImageDraw.Draw(glow)
    gx, gy, gr = 0.88 * W * S, 0.12 * H * S, 340 * S
    for i in range(18, 0, -1):
        r = gr * i / 18
        a = int(40 * (1 - i / 18) ** 1.5)
        gd.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(BG[0] + a, BG[1] + a // 3, BG[2]))
    glow = glow.filter(ImageFilter.GaussianBlur(40 * S))
    return Image.blend(img, glow, 0.55)


def lamp_glow(img, blocks, S):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, z, mat, _ in blocks:
        if mat != "lamp":
            continue
        cx, cy = P(x + 0.5, y + 0.5, z + 0.5, S)
        r = 46 * S
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 170, 60, 70))
    layer = layer.filter(ImageFilter.GaussianBlur(22 * S))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def pill(img, d, x, y, num, title, folder, S, accent=False, anchor=None, align="left"):
    fb = font("Montserrat-Bold.ttf", 17, S)
    fs = font("Aptos-SemiBold.ttf", 14, S)
    num_t, title_t = f"{num}", title
    w_num = d.textlength(num_t, font=fb)
    w_title = d.textlength(title_t, font=fb)
    w_folder = d.textlength(folder, font=fs)
    padx, gap = 14 * S, 10 * S
    w = padx + w_num + 8 * S + w_title + gap + w_folder + padx
    h = 38 * S
    if align == "right":
        x = x - w
    box = [x, y, x + w, y + h]
    if anchor:
        ax, ay = anchor
        lx = x if ax < x else (x + w if ax > x + w else ax)
        ly = y + h / 2 if (ax < x or ax > x + w) else (y + h if ay > y + h else y)
        d.line([(lx, ly), (ax, ay)], fill=(255, 255, 255, 110), width=max(1, int(1.2 * S)))
        rr = 3 * S
        d.ellipse([ax - rr, ay - rr, ax + rr, ay + rr], fill=ORANGE if accent else WHITE)
    d.rounded_rectangle(box, radius=10 * S, fill=CARD + (236,), outline=(255, 255, 255, 28), width=max(1, int(S)))
    ty = y + h / 2
    d.text((x + padx, ty), num_t, font=fb, fill=ORANGE, anchor="lm")
    d.text((x + padx + w_num + 8 * S, ty), title_t, font=fb, fill=WHITE, anchor="lm")
    d.text((x + w - padx, ty + 0.5 * S), folder, font=fs, fill=ORANGE if accent else GREY, anchor="rm")
    return box


LABELS = [  # num, title, folder, pill position (design px), anchor point (grid x, y, z), align, accent
    (1, "Role", "CLAUDE.md", (778, 56), (-2.5, -2.5, 9), "left", True),
    (2, "Tasks", "skills/", (436, 336), (-1, 11, 5), "left", False),
    (3, "Projects", "projects/<name>/", (1226, 60), (5.5, -5.5, 5), "right", False),
    (4, "Knowledge", "learnings/", (420, 154), (-10, 1, 4), "left", False),
    (5, "Tools", "tools/, MCP, hooks", (1232, 416), (10, 2, 5), "right", False),
]


def draw_text_block(d, S, with_title=True):
    f_eye = font("Montserrat-SemiBold.ttf", 12, S)
    f_h1 = font("Montserrat-ExtraBold.ttf", 54, S)
    f_sub = font("Montserrat-Bold.ttf", 22, S)
    f_line = font("Montserrat-SemiBold.ttf", 15, S)
    f_foot = font("Montserrat-SemiBold.ttf", 15, S)
    x = 64 * S
    if with_title:
        d.text((x, 50 * S), "C L A U D E   C O D E   ·   F R E E   S T A R T E R", font=f_eye, fill=ORANGE)
        d.text((x, 76 * S), "Claude\nHomebase", font=f_h1, fill=WHITE, spacing=-4 * S)
        d.text((x, 216 * S), "Build your base, block by block", font=f_sub, fill=ORANGE)
        d.text((x, 252 * S), "One structure for every role:\nrole, tasks, projects, knowledge, tools.", font=f_line,
               fill=GREY, spacing=5 * S)
    d.rectangle([x, 588 * S, (W - 64) * S, 590 * S], fill=ORANGE)
    d.text((x, 603 * S), "antonioblago.com", font=f_foot, fill=WHITE)
    d.text(((W - 64) * S, 603 * S), "github.com/AntonioBlago/claude-homebase  ·  /homebase", font=f_foot, fill=GREY,
           anchor="ra")


def render(blocks, labels_upto, S, with_title=True):
    img = background(S)
    d = ImageDraw.Draw(img)
    for x, y, z, mat, _ in blocks:
        draw_block(d, x, y, z, mat, S)
    img = lamp_glow(img, blocks, S)
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for num, title, folder, (px, py), (ax, ay, az), align, accent in LABELS:
        if num > labels_upto:
            continue
        pill(over, d, px * S, py * S, num, title, folder, S, accent=accent, anchor=P(ax, ay, az, S), align=align)
    draw_text_block(d, S, with_title)
    return Image.alpha_composite(img.convert("RGBA"), over).convert("RGB")


def animation_frames(scene, S, hold_ms=3200):
    """Frames of the build: the island rises layer by layer, then one building after the other, labels appear.
    Returns (frames, durations in ms) at scale S (1.0 = 1280x640)."""
    stages = {}
    for (x, y, z), (mat, st) in scene.blocks.items():
        stages.setdefault(st, []).append((x, y, z))
    frames, durations, shown = [], [], set()
    size = (int(W * S), int(H * S))

    def add(labels_upto, ms):
        frames.append(render(scene.visible(shown), labels_upto, S).resize(size, Image.LANCZOS))
        durations.append(ms)

    for z in sorted({k[2] for k in stages[0]}):
        shown |= {k for k in stages[0] if k[2] == z}
        add(0, 140)
    for st in (1, 2, 3, 4, 5):
        part = stages.get(st, [])
        for z in sorted({k[2] for k in part}):
            shown |= {k for k in part if k[2] == z}
            add(st - 1, 90)
        add(st, 700)                                      # label appears, short hold
    shown |= set(stages.get(6, []))
    add(5, hold_ms)                                       # final hold
    return frames, durations


def main(gif=True):
    scene = build_scene()
    blocks = scene.visible()
    print(f"blocks total {len(scene.blocks)}, visible {len(blocks)}")

    # ---- static PNG, rendered at 2x and downsampled
    S = 2
    img = render(blocks, 5, S)
    img = img.resize((W, H), Image.LANCZOS)
    out_png = os.path.join(HERE, "homebase.png")
    img.save(out_png, optimize=True)
    print("wrote", out_png)
    if not gif:
        return

    # ---- build animation as GIF (960x480)
    frames, durations = animation_frames(scene, 0.75)
    pal = frames[-1].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    out_gif = os.path.join(HERE, "homebase-build.gif")
    q[0].save(out_gif, save_all=True, append_images=q[1:], duration=durations, loop=0, disposal=1, optimize=True)
    print("wrote", out_gif, f"{os.path.getsize(out_gif) / 1e6:.2f} MB, {len(frames)} frames")


if __name__ == "__main__":
    import sys
    main(gif="--no-gif" not in sys.argv)
