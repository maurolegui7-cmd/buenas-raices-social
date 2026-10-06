from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
GREEN = (27, 76, 57)
GOLD = (213, 179, 107)
WHITE = (255, 255, 255)
CREAM = (245, 241, 233)

F = "/usr/share/fonts/opentype/inter/"
f_head = lambda s: ImageFont.truetype(F + "InterDisplay-Bold.otf", s)
f_med = lambda s: ImageFont.truetype(F + "Inter-Medium.otf", s)
f_semi = lambda s: ImageFont.truetype(F + "Inter-SemiBold.otf", s)
f_reg = lambda s: ImageFont.truetype(F + "Inter-Regular.otf", s)


def logo_transparent(path, tol=18):
    """Load logo on white bg, knock out the white to alpha, crop to content."""
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r > 255 - tol and g > 255 - tol and b > 255 - tol:
                px[x, y] = (r, g, b, 0)
    # drop tiny stray marks: keep only the central mark bounding box
    bbox = im.getbbox()
    return im.crop(bbox)


def tracked(draw, xy, text, font, fill, track=0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x


def tracked_width(draw, text, font, track=0):
    return sum(draw.textlength(c, font=font) for c in text) + track * (len(text) - 1)


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


img = Image.new("RGB", (W, H), GREEN)
d = ImageDraw.Draw(img)

M = 96  # margen lateral

# --- franjas doradas inferiores (eco del logo, muy sutiles) ---
band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(band)
for i in range(5):
    r = 760 + i * 135
    cy = H + 250
    bd.arc([W // 2 - r, cy - r // 2, W // 2 + r, cy + r // 2],
           start=185, end=355, fill=GOLD + (30,), width=14)
img.paste(Image.alpha_composite(img.convert("RGBA"), band).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img)

# --- logo ---
logo = logo_transparent("/mnt/user-data/uploads/BR_logo_opcion_4.png")
lh = 132
lw = int(logo.width * lh / logo.height)
logo = logo.resize((lw, lh), Image.LANCZOS)
img.paste(logo, (M, 92), logo)

# --- wordmark al lado del logo ---
wm_x = M + lw + 30
f_wm = f_semi(34)
f_wm2 = f_med(26)
d.text((wm_x, 118), "BUENAS RAÍCES", font=f_wm, fill=WHITE)
tracked(d, (wm_x + 2, 164), "F O R M O S A", f_wm2, GOLD, track=1.5)

# --- etiqueta ---
y = 330
f_tag = f_semi(25)
tag = "P A R A   P R O P I E T A R I O S"
tracked(d, (M, y), tag, f_tag, GOLD, track=1.0)

# --- titular ---
y += 70
f_h = f_head(92)
lines = wrap(d, "¿Tenés una propiedad para vender o alquilar?", f_h, W - 2 * M)
for ln in lines:
    d.text((M, y), ln, font=f_h, fill=WHITE)
    y += 104

# --- filete dorado ---
y += 34
d.rectangle([M, y, M + 120, y + 5], fill=GOLD)

# --- bajada ---
y += 54
f_s = f_reg(40)
sub = "Publicala en el portal inmobiliario de Formosa y llegá a quienes están buscando."
for ln in wrap(d, sub, f_s, W - 2 * M - 40):
    d.text((M, y), ln, font=f_s, fill=(222, 232, 225))
    y += 54

# --- categorías ---
y += 56
f_c = f_med(38)
cats = ["Casas", "Terrenos", "Departamentos"]
cx = M
for i, c in enumerate(cats):
    if i:
        d.ellipse([cx + 2, y + 20, cx + 12, y + 30], fill=GOLD)
        cx += 38
    d.text((cx, y), c, font=f_c, fill=WHITE)
    cx += d.textlength(c, font=f_c) + 24

# --- botón dorado abajo ---
bh, by = 116, H - 96 - 116
d.rounded_rectangle([M, by, W - M, by + bh], radius=bh // 2, fill=GOLD)
f_b = f_semi(42)
btxt = "buenasraicesformosa.com.ar"
bw = d.textlength(btxt, font=f_b)
d.text(((W - bw) / 2, by + (bh - 52) / 2), btxt, font=f_b, fill=GREEN)

img.save("/home/claude/post_instagram_publicar.png", quality=97)
print("ok", img.size)
