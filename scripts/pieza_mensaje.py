"""Piezas de mensaje (consejos, institucional, educativo) para Buenas Raices Formosa."""
from PIL import Image, ImageDraw, ImageFont
from pieza_propiedad import (W, H, GREEN, GREEN_D, GOLD, WHITE,
                             f_head, f_semi, f_med, f_reg,
                             logo_rgba, tracked, wrap)


def build_mensaje(out, etiqueta, titulo, bajada, puntos, cierre,
                  invertido=False):
    """invertido=True -> fondo claro con texto verde (para variar el feed)."""
    bg = (245, 241, 233) if invertido else GREEN
    fg = GREEN if invertido else WHITE
    soft = (74, 110, 92) if invertido else (209, 224, 215)
    card = (235, 228, 214) if invertido else GREEN_D

    img = Image.new("RGB", (W, H), bg)

    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    alpha = 46 if invertido else 30
    for i in range(5):
        r = 760 + i * 135
        cy = H + 250
        bd.arc([W // 2 - r, cy - r // 2, W // 2 + r, cy + r // 2],
               start=185, end=355, fill=GOLD + (alpha,), width=14)
    img = Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")
    d = ImageDraw.Draw(img)

    M = 90

    # logo + wordmark
    lg = logo_rgba()
    lh = 104
    lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
    img.paste(lg, (M, 80), lg)
    wx = M + lg.width + 26
    d.text((wx, 98), "BUENAS RAÍCES", font=f_semi(29), fill=fg)
    tracked(d, (wx + 2, 136), "F O R M O S A", f_med(22),
            (154, 120, 48) if invertido else GOLD, track=1.3)

    # etiqueta
    y = 290
    tracked(d, (M, y), etiqueta, f_semi(25),
            (154, 120, 48) if invertido else GOLD, track=1.0)

    # titular
    y += 66
    f_t = f_head(78)
    for ln in wrap(d, titulo, f_t, W - 2 * M)[:4]:
        d.text((M, y), ln, font=f_t, fill=fg)
        y += 90

    # filete
    y += 24
    d.rectangle([M, y, M + 120, y + 5], fill=GOLD)
    y += 50

    # bajada
    if bajada:
        f_b = f_reg(37)
        for ln in wrap(d, bajada, f_b, W - 2 * M - 20):
            d.text((M, y), ln, font=f_b, fill=soft)
            y += 50
        y += 24

    # puntos
    f_p = f_med(35)
    for p in puntos:
        d.rounded_rectangle([M, y, W - M, y + 86], radius=18, fill=card)
        d.ellipse([M + 30, y + 37, M + 44, y + 51], fill=GOLD)
        d.text((M + 68, y + 24), p, font=f_p, fill=fg)
        y += 100

    # cierre (sólo si no pisa las tarjetas)
    bh, by = 112, H - 92 - 112
    if cierre:
        f_c = f_semi(36)
        cy = by - 92
        if cy >= y + 16:
            cw_ = d.textlength(cierre, font=f_c)
            d.text(((W - cw_) / 2, cy), cierre, font=f_c, fill=fg)

    d.rounded_rectangle([M, by, W - M, by + bh], radius=bh // 2, fill=GOLD)
    f_bt = f_semi(42)
    bt = "buenasraicesformosa.com.ar"
    bw = d.textlength(bt, font=f_bt)
    d.text(((W - bw) / 2, by + (bh - 52) / 2), bt, font=f_bt, fill=GREEN)

    img.save(out, quality=97)
    print("ok", out)
