"""Historias de Instagram 1080x1920 para Buenas Raices Formosa.

Cuatro plantillas, pensadas para rotar y que una historia por dia sea
sostenible sin inventar contenido nuevo todos los dias:

  amplifica   lun/mie/vie: muestra el posteo del feed de ese dia
  tasador     empuja /tasador; deja la franja inferior libre para el sticker
  propiedad   una propiedad del portal con su foto real
  tip         una sola idea, en tipografia grande

Zona segura: Instagram superpone su interfaz arriba (~250 px, foto de perfil)
y abajo (~250 px, barra de respuesta). Todo el contenido vive entre y=300 e
y=1620. Las historias de tasador reservan ademas la franja 1250-1620 para el
sticker de link, que se agrega a mano al publicar.
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pieza_propiedad import (GREEN, GREEN_D, GOLD, WHITE,
                             f_head, f_semi, f_med, f_reg,
                             logo_rgba, tracked, wrap)

W, H = 1080, 1920
M = 96
SOFT = (209, 224, 215)
TOP, BOTTOM = 300, 1620


def _fondo():
    img = Image.new("RGB", (W, H), GREEN)
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(6):
        r = 820 + i * 150
        cy = H + 240
        bd.arc([W // 2 - r, cy - r // 2, W // 2 + r, cy + r // 2],
               start=185, end=355, fill=GOLD + (30,), width=15)
    return Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")


def _marca(d, img, y=TOP):
    lg = logo_rgba()
    lh = 92
    lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
    img.paste(lg, (M, y), lg)
    wx = M + lg.width + 24
    d.text((wx, y + 14), "BUENAS RAÍCES", font=f_semi(27), fill=WHITE)
    tracked(d, (wx + 2, y + 50), "F O R M O S A", f_med(20), GOLD, track=1.3)
    return y + lh


def _boton(d, y, texto, ancho=None):
    f = f_semi(38)
    alto = 112
    ancho = ancho or (W - 2 * M)
    x0 = (W - ancho) // 2
    d.rounded_rectangle([x0, y, x0 + ancho, y + alto], radius=alto // 2,
                        fill=GOLD)
    tw = d.textlength(texto, font=f)
    d.text(((W - tw) / 2, y + (alto - 50) / 2), texto, font=f, fill=GREEN)


def _scrim_foto():
    sc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = sc.load()
    for y in range(H):
        if y < 520:
            a = int(210 * (1 - y / 520.0))
        elif y < 980:
            a = 0
        elif y < 1180:
            a = int(246 * ((y - 980) / 200.0))
        else:
            a = 246
        if a:
            fila = GREEN_D + (a,)
            for x in range(W):
                px[x, y] = fila
    return sc


def _foto_9x16(ruta):
    im = Image.open(ruta).convert("RGB")
    objetivo = W / H
    if im.width / im.height > objetivo:
        nw = int(im.height * objetivo)
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(im.width / objetivo)
        y = int((im.height - nh) * 0.38)
        im = im.crop((0, y, im.width, y + nh))
    return im.resize((W, H), Image.LANCZOS)


# ------------------------------------------------------------- plantillas

def historia_amplifica(out, etiqueta, titulo, preview, cta="Mirá el posteo completo"):
    """Historia que muestra el posteo del feed de ese dia.

    Dos modos segun la forma del posteo que amplifica:
      - vertical (cuadro de un Reel, 9:16): se usa a sangre como fondo. Una
        vista previa 9:16 dentro de una historia 9:16 metida en una tarjeta
        queda ridiculamente chica, asi que ocupa toda la pantalla.
      - 4:5 o mas ancho (una placa del feed): tarjeta centrada con borde
        dorado, que es como se ve un posteo en el feed.
    """
    pv = Image.open(preview).convert("RGB")
    vertical = (pv.height / pv.width) >= 1.4

    if vertical:
        base = _foto_9x16(preview)
        img = Image.alpha_composite(base.convert("RGBA"),
                                    _scrim_foto()).convert("RGB")
        d = ImageDraw.Draw(img)
        _marca(d, img)
        y = 1210
        tracked(d, (M, y), etiqueta, f_semi(26), GOLD, track=1.1)
        y += 60
        f = f_head(58)
        for ln in wrap(d, titulo, f, W - 2 * M)[:2]:
            d.text((M, y), ln, font=f, fill=WHITE)
            y += 68
        _boton(d, 1480, cta)
    else:
        img = _fondo()
        d = ImageDraw.Draw(img)
        y = _marca(d, img) + 56

        tracked(d, (M, y), etiqueta, f_semi(26), GOLD, track=1.1)
        y += 56
        f = f_head(58)
        for ln in wrap(d, titulo, f, W - 2 * M)[:2]:
            d.text((M, y), ln, font=f, fill=WHITE)
            y += 68
        y += 34

        cw = W - 2 * M - 40
        ch = int(pv.height * cw / pv.width)
        maxh = 1400 - y
        if ch > maxh:
            ch = maxh
            cw = int(pv.width * ch / pv.height)
        pv = pv.resize((cw, ch), Image.LANCZOS)
        mask = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, ch], radius=26,
                                               fill=255)
        px = (W - cw) // 2
        d.rounded_rectangle([px - 5, y - 5, px + cw + 5, y + ch + 5],
                            radius=31, fill=GOLD)
        img.paste(pv, (px, y), mask)
        _boton(d, max(y + ch + 46, 1460), cta)

    img.save(out, quality=96)
    print("ok", out)


def historia_tasador(out, titulo, bajada, pie="Tocá el link de abajo"):
    """Historia del tasador. Deja 1250-1620 libre para el sticker de link."""
    img = _fondo()
    d = ImageDraw.Draw(img)
    y = _marca(d, img) + 110

    tracked(d, (M, y), "TASADOR ONLINE", f_semi(26), GOLD, track=1.1)
    y += 64
    f = f_head(88)
    for ln in wrap(d, titulo, f, W - 2 * M)[:4]:
        d.text((M, y), ln, font=f, fill=WHITE)
        y += 102
    y += 24
    d.rectangle([M, y, M + 130, y + 6], fill=GOLD)
    y += 54
    f2 = f_reg(40)
    for ln in wrap(d, bajada, f2, W - 2 * M)[:3]:
        d.text((M, y), ln, font=f2, fill=SOFT)
        y += 54

    # pie, justo arriba de la franja reservada al sticker
    f3 = f_semi(34)
    tw = d.textlength(pie, font=f3)
    d.text(((W - tw) / 2, 1180), pie, font=f3, fill=GOLD)
    img.save(out, quality=96)
    print("ok", out)


def historia_propiedad(out, ruta_foto, operacion, precio, titulo, direccion):
    """Historia de una propiedad, con la foto real del aviso."""
    base = _foto_9x16(ruta_foto)
    img = Image.alpha_composite(base.convert("RGBA"), _scrim_foto()).convert("RGB")
    d = ImageDraw.Draw(img)
    _marca(d, img)

    y = 1110
    f = f_semi(26)
    cw = d.textlength(operacion, font=f) + 44
    d.rounded_rectangle([M, y, M + cw, y + 56], radius=28, fill=GOLD)
    d.text((M + 22, y + 13), operacion, font=f, fill=GREEN)
    y += 84

    fp = f_head(92)
    d.text((M, y), precio, font=fp, fill=GOLD)
    y += 112
    ft = f_head(50)
    for ln in wrap(d, titulo, ft, W - 2 * M)[:2]:
        d.text((M, y), ln, font=ft, fill=WHITE)
        y += 60
    fd = f_reg(34)
    for ln in wrap(d, direccion, fd, W - 2 * M)[:2]:
        d.text((M, y), ln, font=fd, fill=SOFT)
        y += 44

    _boton(d, 1480, "Ver el aviso en el portal")
    img.save(out, quality=96)
    print("ok", out)


def historia_tip(out, etiqueta, texto, pie=""):
    """Historia de una sola idea, en tipografia grande."""
    img = _fondo()
    d = ImageDraw.Draw(img)
    _marca(d, img)

    f = f_head(84)
    lineas = wrap(d, texto, f, W - 2 * M)[:6]
    y = (H - len(lineas) * 100) // 2 - 60
    tracked(d, (M, y - 80), etiqueta, f_semi(26), GOLD, track=1.1)
    for ln in lineas:
        d.text((M, y), ln, font=f, fill=WHITE)
        y += 100
    y += 24
    d.rectangle([M, y, M + 130, y + 6], fill=GOLD)

    if pie:
        f2 = f_reg(36)
        yy = y + 60
        for ln in wrap(d, pie, f2, W - 2 * M)[:3]:
            d.text((M, yy), ln, font=f2, fill=SOFT)
            yy += 50

    f3 = f_semi(32)
    t = "buenasraicesformosa.com.ar"
    tw = d.textlength(t, font=f3)
    d.text(((W - tw) / 2, 1540), t, font=f3, fill=GOLD)
    img.save(out, quality=96)
    print("ok", out)
