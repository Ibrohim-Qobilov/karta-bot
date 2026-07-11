#!/usr/bin/env python3
"""Karta Bot uchun rasmlar: botpic (512x512), description (640x360), banner (1280x400)."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = Image.Resampling
OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

INDIGO_DARK = (15, 17, 52)
INDIGO = (67, 56, 202)
CYAN = (8, 145, 178)


# ---------------- helpers ----------------

def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def diag_gradient(w, h, stops):
    """Diagonal (chapdan-yuqoridan o'ngga-pastga) gradient."""
    n = 128
    img = Image.new("RGB", (n, n))
    px = img.load()
    m = len(stops) - 1
    for y in range(n):
        for x in range(n):
            t = (x / (n - 1) + y / (n - 1)) / 2 * m
            i = min(int(t), m - 1)
            px[x, y] = lerp(stops[i], stops[i + 1], t - i)
    return img.resize((w, h), R.BICUBIC).convert("RGBA")


def quad(p0, p1, p2, n=28):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        pts.append((
            (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1],
        ))
    return pts


def shield_pts(cx, cy, sw, sh, scale=1.0):
    """Qalqon konturi (markazga nisbatan)."""
    u = []
    u += quad((0.06, 0.16), (0.06, 0.05), (0.17, 0.045))          # chap-yuqori burchak
    u += [(0.83, 0.045)]                                          # tepa chiziq
    u += quad((0.83, 0.045), (0.94, 0.05), (0.94, 0.16))          # o'ng-yuqori burchak
    u += [(0.94, 0.44)]                                           # o'ng yon
    u += quad((0.94, 0.44), (0.92, 0.76), (0.50, 0.985))          # o'ng qorin
    u += quad((0.50, 0.985), (0.08, 0.76), (0.06, 0.44))          # chap qorin
    u += [(0.06, 0.16)]
    return [(cx + (x - 0.5) * sw * scale, cy + (y - 0.5) * sh * scale) for x, y in u]


def find_font(size, bold=True):
    tries = [
        ("/System/Library/Fonts/Avenir Next.ttc",
         ("Bold", "Demi Bold") if bold else ("Medium", "Regular")),
        ("/System/Library/Fonts/HelveticaNeue.ttc",
         ("Bold",) if bold else ("Regular",)),
        ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold
         else "/System/Library/Fonts/Supplemental/Arial.ttf", None),
    ]
    for path, styles in tries:
        try:
            if styles is None:
                return ImageFont.truetype(path, size)
            for i in range(30):
                try:
                    f = ImageFont.truetype(path, size, index=i)
                except Exception:
                    break
                if f.getname()[1] in styles:
                    return f
        except Exception:
            continue
    return ImageFont.load_default()


# ---------------- card + shield logo ----------------

def make_card(cw):
    ch = round(cw / 1.586)
    rad = round(cw * 0.075)
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    face = diag_gradient(cw, ch, [(255, 255, 255), (224, 229, 247)])
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=rad, fill=255)
    card.paste(face, (0, 0), mask)
    d = ImageDraw.Draw(card)

    # brend chizig'i (yuqori chapda, indigo pill)
    d.rounded_rectangle([cw * 0.085, ch * 0.085, cw * 0.30, ch * 0.155],
                        radius=ch * 0.035, fill=(99, 102, 241))

    # chip
    chx, chy = cw * 0.085, ch * 0.28
    chw, chh = cw * 0.155, cw * 0.115
    lw = max(2, round(cw * 0.006))
    d.rounded_rectangle([chx, chy, chx + chw, chy + chh], radius=chw * 0.22,
                        fill=(246, 190, 50), outline=(196, 124, 14), width=lw)
    d.line([chx, chy + chh * 0.38, chx + chw, chy + chh * 0.38], fill=(196, 124, 14), width=lw)
    d.line([chx, chy + chh * 0.66, chx + chw, chy + chh * 0.66], fill=(196, 124, 14), width=lw)
    d.line([chx + chw * 0.5, chy, chx + chw * 0.5, chy + chh], fill=(196, 124, 14), width=lw)

    # contactless to'lqinlar
    ax, ay = cw * 0.82, ch * 0.36
    for rr in (cw * 0.030, cw * 0.055, cw * 0.080):
        d.arc([ax - rr, ay - rr, ax + rr, ay + rr], start=-42, end=42,
              fill=(148, 163, 184), width=max(3, round(cw * 0.013)))

    # karta raqami — nuqtalar
    dd = cw * 0.030
    gap_in, gap_g = dd * 0.55, dd * 1.4
    total = 4 * (4 * dd + 3 * gap_in) + 3 * gap_g
    x = (cw - total) / 2
    y = ch * 0.60
    for g in range(4):
        for i in range(4):
            d.ellipse([x, y, x + dd, y + dd], fill=(71, 85, 105))
            x += dd + (gap_in if i < 3 else 0)
        x += gap_g

    # karta egasi — kulrang pill
    d.rounded_rectangle([cw * 0.085, ch * 0.795, cw * 0.42, ch * 0.865],
                        radius=ch * 0.035, fill=(203, 213, 225))
    return card


def make_shield(sw):
    sh = round(sw * 1.08)
    pad = round(sw * 0.16)
    W, H = sw + 2 * pad, sh + 2 * pad
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H / 2

    # oq hoshiya (kattaroq qalqon)
    d.polygon(shield_pts(cx, cy, sw, sh, 1.13), fill=(255, 255, 255))
    # yashil qalqon — gradient
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(shield_pts(cx, cy, sw, sh), fill=255)
    face = diag_gradient(W, H, [(52, 211, 153), (5, 150, 105)])
    img.paste(face, (0, 0), mask)
    d = ImageDraw.Draw(img)

    # qulf — oq
    lw = max(3, round(sw * 0.058))
    shx0, shy0 = cx - sw * 0.16, cy - sh * 0.28
    shx1, shy1 = cx + sw * 0.16, cy + sh * 0.14
    d.arc([shx0, shy0, shx1, shy1], start=180, end=360, fill=(255, 255, 255), width=lw)
    bw, bh = sw * 0.40, sh * 0.30
    by0 = cy - sh * 0.07
    d.rounded_rectangle([cx - bw / 2, by0, cx + bw / 2, by0 + bh],
                        radius=sw * 0.055, fill=(255, 255, 255))
    # kalit teshigi
    kr = sw * 0.045
    kcy = by0 + bh * 0.38
    d.ellipse([cx - kr, kcy - kr, cx + kr, kcy + kr], fill=(4, 120, 87))
    d.rounded_rectangle([cx - kr * 0.45, kcy, cx + kr * 0.45, kcy + bh * 0.34],
                        radius=kr * 0.4, fill=(4, 120, 87))
    return img


def make_logo(cw, angle=9):
    """Egilgan karta + qalqon, soyalar bilan (shaffof fonda)."""
    card = make_card(cw)
    rot = card.rotate(angle, expand=True, resample=R.BICUBIC)
    W = rot.width + round(cw * 0.30)
    H = rot.height + round(cw * 0.34)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px, py = (W - rot.width) // 2, (H - rot.height) // 2 - round(cw * 0.03)

    # karta soyasi
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    black = Image.new("RGBA", rot.size, (8, 12, 38, 150))
    shadow.paste(black, (px, py + round(cw * 0.05)), rot.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(cw * 0.035))
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.alpha_composite(rot, (px, py))

    # qalqon — o'ng-past burchakda
    sh_img = make_shield(round(cw * 0.40))
    sx = px + rot.width - round(sh_img.width * 0.78)
    sy = py + rot.height - round(sh_img.height * 0.72)
    sh_shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    black2 = Image.new("RGBA", sh_img.size, (8, 12, 38, 140))
    sh_shadow.paste(black2, (sx, sy + round(cw * 0.03)), sh_img.split()[3])
    sh_shadow = sh_shadow.filter(ImageFilter.GaussianBlur(cw * 0.025))
    canvas = Image.alpha_composite(canvas, sh_shadow)
    canvas.alpha_composite(sh_img, (sx, sy))
    return canvas


# ---------------- backgrounds ----------------

def make_bg(w, h):
    bg = diag_gradient(w, h, [INDIGO_DARK, INDIGO, CYAN])
    over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    ring_w = max(2, round(min(w, h) * 0.012))
    r1 = min(w, h) * 0.42
    d.ellipse([w * 0.04 - r1, h * 0.10 - r1, w * 0.04 + r1, h * 0.10 + r1],
              outline=(255, 255, 255, 22), width=ring_w)
    r2 = min(w, h) * 0.55
    d.ellipse([w * 0.97 - r2, h * 0.95 - r2, w * 0.97 + r2, h * 0.95 + r2],
              outline=(255, 255, 255, 20), width=ring_w)
    return Image.alpha_composite(bg, over)


def add_glow(img, cx, cy, r, alpha=60):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - r, cy - r, cx + r, cy + r],
                                 fill=(190, 210, 255, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(r * 0.45))
    return Image.alpha_composite(img, glow)


def paste_center(base, layer, cx, cy):
    base.alpha_composite(layer, (round(cx - layer.width / 2), round(cy - layer.height / 2)))


# ---------------- 1) botpic 512x512 ----------------

def gen_botpic():
    S = 2048
    img = make_bg(S, S)
    img = add_glow(img, S * 0.5, S * 0.46, S * 0.36, 55)
    logo = make_logo(round(S * 0.60))
    paste_center(img, logo, S * 0.5, S * 0.485)
    img.convert("RGB").resize((512, 512), R.LANCZOS).save(f"{OUT}/botpic.png")
    print("botpic.png ✅")


# ---------------- 2) description pic 640x360 ----------------

def gen_description():
    W, H = 1920, 1080
    img = make_bg(W, H)
    img = add_glow(img, W * 0.24, H * 0.52, W * 0.17, 45)
    logo = make_logo(560)
    paste_center(img, logo, W * 0.245, H * 0.53)

    d = ImageDraw.Draw(img)
    x = W * 0.475
    f_title = find_font(172, bold=True)
    f_tag = find_font(74, bold=True)
    feat_txt = "Shifrlash  •  PIN-himoya  •  8 til  •  Inline qidiruv"
    size = 48
    while size > 34 and d.textlength(feat_txt, font=find_font(size, False)) > W - x - 50:
        size -= 2
    f_feat = find_font(size, bold=False)
    f_pill = find_font(58, bold=True)

    d.text((x, H * 0.245), "Karta Bot", font=f_title, fill=(255, 255, 255), anchor="lm")
    d.text((x, H * 0.425), "Bank kartalaringiz —", font=f_tag, fill=(224, 231, 255), anchor="lm")
    d.text((x, H * 0.525), "bitta xavfsiz joyda", font=f_tag, fill=(224, 231, 255), anchor="lm")
    d.text((x, H * 0.655), feat_txt, font=f_feat, fill=(165, 180, 252), anchor="lm")

    # pill — yarim-shaffof fonni alpha_composite bilan qo'yamiz
    pill_txt = "@tezkartabot"
    tw = d.textlength(pill_txt, font=f_pill)
    py0, py1 = H * 0.745, H * 0.865
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(over).rounded_rectangle(
        [x, py0, x + tw + 84, py1], radius=(py1 - py0) / 2,
        fill=(255, 255, 255, 36), outline=(255, 255, 255, 110), width=3)
    img = Image.alpha_composite(img, over)
    ImageDraw.Draw(img).text((x + 42, (py0 + py1) / 2), pill_txt,
                             font=f_pill, fill=(255, 255, 255), anchor="lm")

    img.convert("RGB").resize((640, 360), R.LANCZOS).save(f"{OUT}/description.png")
    print("description.png ✅")


# ---------------- 3) banner 1280x400 ----------------

def gen_banner():
    W, H = 2560, 800
    img = make_bg(W, H)
    img = add_glow(img, W * 0.80, H * 0.55, H * 0.42, 45)
    logo = make_logo(600)
    paste_center(img, logo, W * 0.795, H * 0.54)

    d = ImageDraw.Draw(img)
    x = 150
    f_title = find_font(185, bold=True)
    f_tag = find_font(72, bold=True)
    f_feat = find_font(50, bold=False)

    d.text((x, H * 0.315), "Karta Bot", font=f_title, fill=(255, 255, 255), anchor="lm")
    d.text((x, H * 0.565), "Bank kartalaringiz — bitta xavfsiz joyda",
           font=f_tag, fill=(224, 231, 255), anchor="lm")
    d.text((x, H * 0.735), "Shifrlash  •  PIN-himoya  •  8 til  •  Inline qidiruv",
           font=f_feat, fill=(165, 180, 252), anchor="lm")

    img.convert("RGB").resize((1280, 400), R.LANCZOS).save(f"{OUT}/banner.png")
    print("banner.png ✅")


if __name__ == "__main__":
    gen_botpic()
    gen_description()
    gen_banner()
