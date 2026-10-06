"""Genera piezas de Instagram para propiedades destacadas de Buenas Raices Formosa."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
GREEN = (27, 76, 57)
GREEN_D = (16, 48, 35)
GOLD = (213, 179, 107)
WHITE = (255, 255, 255)

F = "/usr/share/fonts/opentype/inter/"
f_head = lambda s: ImageFont.truetype(F + "InterDisplay-Bold.otf", s)
f_semi = lambda s: ImageFont.truetype(F + "Inter-SemiBold.otf", s)
f_med = lambda s: ImageFont.truetype(F + "Inter-Medium.otf", s)
f_reg = lambda s: ImageFont.truetype(F + "Inter-Regular.otf", s)

_LOGO = None


def logo_rgba():
    global _LOGO
    if _LOGO is None:
        im = Image.open("/mnt/user-data/uploads/BR_logo_opcion_4.png").convert("RGBA")
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if r > 237 and g > 237 and b > 237:
                    px[x, y] = (r, g, b, 0)
        _LOGO = im.crop(im.getbbox())
    return _LOGO


def tracked(d, xy, text, font, fill, track=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track


def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def build(out, operacion, titulo, precio, direccion, specs, destacados):
    """specs: lista de (valor, etiqueta). destacados: hasta 3 strings cortos."""
    img = Image.new("RGB", (W, H), GREEN)
    d = ImageDraw.Draw(img)
    M = 90

    # arcos sutiles al pie
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(5):
        r = 760 + i * 135
        cy = H + 250
        bd.arc([W // 2 - r, cy - r // 2, W // 2 + r, cy + r // 2],
               start=185, end=355, fill=GOLD + (30,), width=14)
    img = Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")
    d = ImageDraw.Draw(img)

    # logo + wordmark
    lg = logo_rgba()
    lh = 104
    lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
    img.paste(lg, (M, 80), lg)
    wx = M + lg.width + 26
    d.text((wx, 98), "BUENAS RAÍCES", font=f_semi(29), fill=WHITE)
    tracked(d, (wx + 2, 136), "F O R M O S A", f_med(22), GOLD, track=1.3)

    # chip de operación
    f_op = f_semi(26)
    ow = d.textlength(operacion, font=f_op)
    d.rounded_rectangle([W - M - ow - 48, 96, W - M, 96 + 56], radius=28, fill=GOLD)
    d.text((W - M - ow - 24, 108), operacion, font=f_op, fill=GREEN)

    # precio
    y = 300
    f_p = f_head(86)
    d.text((M, y), precio, font=f_p, fill=GOLD)
    y += 118

    # título
    f_t = f_head(50)
    for ln in wrap(d, titulo, f_t, W - 2 * M)[:3]:
        d.text((M, y), ln, font=f_t, fill=WHITE)
        y += 62

    # dirección
    y += 18
    f_d = f_reg(34)
    for ln in wrap(d, direccion, f_d, W - 2 * M)[:2]:
        d.text((M, y), ln, font=f_d, fill=(196, 214, 203))
        y += 44

    # tarjetas de specs
    y += 44
    n = len(specs)
    gap = 18
    cw = (W - 2 * M - gap * (n - 1)) // n
    ch = 150
    for i, (val, lab) in enumerate(specs):
        x = M + i * (cw + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=20, fill=GREEN_D)
        f_v = f_head(46)
        vw = d.textlength(val, font=f_v)
        d.text((x + (cw - vw) / 2, y + 30), val, font=f_v, fill=WHITE)
        f_l = f_med(25)
        lw = d.textlength(lab, font=f_l)
        d.text((x + (cw - lw) / 2, y + 92), lab, font=f_l, fill=GOLD)
    y += ch + 46

    # destacados
    f_f = f_med(33)
    for item in destacados[:3]:
        d.ellipse([M + 3, y + 13, M + 15, y + 25], fill=GOLD)
        d.text((M + 36, y), item, font=f_f, fill=(226, 236, 230))
        y += 50

    # botón
    bh, by = 112, H - 92 - 112
    d.rounded_rectangle([M, by, W - M, by + bh], radius=bh // 2, fill=GOLD)
    f_b = f_semi(40)
    bt = "Ver el aviso en buenasraicesformosa.com.ar"
    bw = d.textlength(bt, font=f_b)
    d.text(((W - bw) / 2, by + (bh - 50) / 2), bt, font=f_b, fill=GREEN)

    img.save(out, quality=97)
    print("ok", out)
