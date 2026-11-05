"""Reels verticales 1080x1920 de propiedades, con la foto real del aviso.

La foto es la que cargo el publicante (`coverImageUrl` de la API): no se
genera ni se retoca contenido, solo se le agrega movimiento (Ken Burns) y se
sobreimprimen los datos con la identidad de la marca.

Estructura: foto con zoom lento y los datos del aviso encima, transicion al
verde de marca para las caracteristicas y el cierre con boton.

Uso:
    from reel_propiedad import build_reel_propiedad
    build_reel_propiedad(carpeta, "salida.mp4", "foto.jpg",
                         operacion="VENTA", precio="U$D 298.000",
                         titulo="Penthouse con terraza propia",
                         direccion="Av. Dr. Néstor Kirchner 2965, Formosa capital",
                         specs=[("4", "ambientes"), ("192,3", "m² totales"),
                                ("1", "cochera")],
                         caracteristicas=["terraza privada con parrilla y jacuzzi",
                                          "dormitorio principal en suite",
                                          "climatización en todos los ambientes"])
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pieza_propiedad import (GREEN, GREEN_D, GOLD, WHITE,
                             f_head, f_semi, f_med, f_reg, wrap)
from reel_captacion import (W, H, FPS, M, SOFT,
                            fade_in, blend, base_bg, draw_marca,
                            texto_animado, boton, tracked)

# (inicio, duracion) en frames a 30 fps
S1 = (0, 150)      # foto + operacion + precio + titulo
S2 = (150, 120)    # foto + specs
S3 = (270, 105)    # verde + caracteristicas
S4 = (375, 75)     # verde + cierre
TOTAL = 450        # 15 s
FADE = 18          # frames de crossfade foto -> verde

ZOOM = 1.18        # factor de zoom-out inicial del Ken Burns


def preparar_foto(ruta):
    """Recorta la foto a 9:16 y la deja a la resolucion de trabajo."""
    im = Image.open(ruta).convert("RGB")
    objetivo = W / H
    if im.width / im.height > objetivo:        # mas ancha: recorto a los lados
        nw = int(im.height * objetivo)
        x = (im.width - nw) // 2
        im = im.crop((x, 0, x + nw, im.height))
    else:                                       # mas alta: recorto arriba/abajo
        nh = int(im.width / objetivo)
        y = int((im.height - nh) * 0.42)        # leve sesgo hacia arriba
        im = im.crop((0, y, im.width, y + nh))
    return im.resize((int(W * ZOOM), int(H * ZOOM)), Image.LANCZOS)


def _scrim():
    """Degrade verde oscuro arriba y abajo, para que el texto se lea.

    Abajo llega casi opaco a la altura del bloque de datos (y>=1000): la foto
    se luce en la mitad superior y el texto siempre cae sobre fondo solido,
    sin depender de que la foto sea clara u oscura ahi.
    """
    sc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = sc.load()
    for y in range(H):
        a_top = max(0, int(200 * (1 - y / 560.0))) if y < 560 else 0
        if y < 820:
            a_bot = 0
        elif y < 1010:
            a_bot = int(246 * ((y - 820) / 190.0))
        else:
            a_bot = 246
        a = min(246, max(a_top, a_bot))
        if a:
            fila = GREEN_D + (a,)
            for x in range(W):
                px[x, y] = fila
    return sc


def frame_foto(foto, scrim, t):
    """Frame de fondo con Ken Burns: t en [0,1] a lo largo de toda la parte foto."""
    k = ZOOM - (ZOOM - 1.0) * t          # de ZOOM a 1.0: acerca lentamente
    cw, ch = int(W * k), int(H * k)
    x = (foto.width - cw) // 2
    y = int((foto.height - ch) * (0.5 + 0.08 * t))   # leve deriva hacia abajo
    vista = foto.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(vista.convert("RGBA"), scrim).convert("RGB")


def chip(d, x, y, texto):
    """Chip dorado de operacion (VENTA / ALQUILER)."""
    f = f_semi(28)
    tw = d.textlength(texto, font=f) + 24 * 2
    d.rounded_rectangle([x, y, x + tw, y + 60], radius=30, fill=GOLD)
    d.text((x + 24, y + 13), texto, font=f, fill=GREEN)
    return y + 60


def tarjeta_spec(d, x, y, ancho, valor, etiqueta, prog, fondo=GREEN_D):
    if prog <= 0:
        return
    a = prog
    dy = int(40 * (1 - a))
    alto = 150
    d.rounded_rectangle([x, y + dy, x + ancho, y + dy + alto], radius=20,
                        fill=blend(fondo, GREEN, a))
    fv = f_head(46)
    vw = d.textlength(valor, font=fv)
    d.text((x + (ancho - vw) / 2, y + dy + 32), valor, font=fv,
           fill=blend(GOLD, GREEN, a))
    fe = f_med(26)
    ew = d.textlength(etiqueta, font=fe)
    d.text((x + (ancho - ew) / 2, y + dy + 94), etiqueta, font=fe,
           fill=blend(WHITE, GREEN, a))


def render_frame(n, foto, scrim, verde, operacion, precio, titulo, direccion,
                 specs, caracteristicas):
    fin_foto = S3[0]
    if n < fin_foto:
        img = frame_foto(foto, scrim, n / float(fin_foto))
    elif n < fin_foto + FADE:
        a = (n - fin_foto) / float(FADE)
        img = Image.blend(frame_foto(foto, scrim, 1.0), verde, a)
    else:
        img = verde.copy()

    d = ImageDraw.Draw(img)
    draw_marca(d, img, min(1.0, fade_in(n, 0, 20)))

    # --- Escena 1: operacion, precio, titulo, direccion -------------------
    if n < S2[0]:
        p = fade_in(n, 14, 30)
        if p > 0.02:
            y = 1030
            chip(d, M, y, operacion)
            fp = f_head(104)
            texto_animado(d, [precio], fp, y + 92, 118, fade_in(n, 24, 34),
                          GOLD, dy=40)
            ft = f_head(58)
            lt = wrap(d, titulo, ft, W - 2 * M)[:2]
            texto_animado(d, lt, ft, y + 226, 68, fade_in(n, 38, 34), WHITE,
                          dy=36)
            fd = f_reg(36)
            ld = wrap(d, direccion, fd, W - 2 * M)[:2]
            texto_animado(d, ld, fd, y + 226 + 68 * len(lt) + 20, 48,
                          fade_in(n, 52, 30), SOFT, dy=30)

    # --- Escena 2: specs --------------------------------------------------
    elif n < S3[0]:
        k = n - S2[0]
        y = 1180
        hueco = 18
        ancho = (W - 2 * M - hueco * (len(specs) - 1)) // len(specs)
        for i, (valor, etiqueta) in enumerate(specs):
            tarjeta_spec(d, M + i * (ancho + hueco), y, ancho, valor, etiqueta,
                         fade_in(k, i * 14, 28))
        fd = f_reg(36)
        texto_animado(d, wrap(d, direccion, fd, W - 2 * M)[:2], fd,
                      y + 190, 48, fade_in(k, 50, 30), SOFT, dy=28)

    # --- Escena 3: caracteristicas ---------------------------------------
    elif n < S4[0]:
        k = n - S3[0]
        tracked(d, (M, 560), "SEGÚN EL AVISO", f_semi(27), GOLD, track=1.1)
        y = 660
        f = f_med(40)
        for i, c in enumerate(caracteristicas[:3]):
            pr = fade_in(k, 12 + i * 22, 28)
            if pr <= 0:
                continue
            dx = int(50 * (1 - pr))
            d.rounded_rectangle([M + dx, y, W - M + dx, y + 140], radius=22,
                                fill=blend(GREEN_D, GREEN, pr))
            cy = y + 70
            d.ellipse([M + dx + 46, cy - 11, M + dx + 68, cy + 11],
                      fill=blend(GOLD, GREEN, pr))
            lineas = wrap(d, c, f, W - 2 * M - 150)[:2]
            ty = cy - len(lineas) * 24
            for ln in lineas:
                d.text((M + dx + 104, ty), ln, font=f,
                       fill=blend(WHITE, GREEN, pr))
                ty += 48
            y += 168

    # --- Escena 4: cierre -------------------------------------------------
    else:
        k = n - S4[0]
        p = fade_in(k, 0, 28)
        f = f_head(72)
        texto_animado(d, ["Mirá el aviso", "completo"], f, 700, 86, p, WHITE)
        f2 = f_reg(38)
        texto_animado(d, ["El contacto es directo con quien publica."],
                      f2, 900, 52, fade_in(k, 18, 28), SOFT)
        boton(d, 1100, fade_in(k, 30, 32))

    return img


def build_reel_propiedad(carpeta, salida, ruta_foto, operacion, precio, titulo,
                         direccion, specs, caracteristicas):
    os.makedirs(carpeta, exist_ok=True)
    for f in os.listdir(carpeta):
        if f.endswith(".png"):
            os.remove(os.path.join(carpeta, f))
    foto = preparar_foto(ruta_foto)
    scrim = _scrim()
    verde = base_bg()
    for n in range(TOTAL):
        render_frame(n, foto, scrim, verde, operacion, precio, titulo,
                     direccion, specs, caracteristicas).save(
            os.path.join(carpeta, "f%04d.png" % n))
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", os.path.join(carpeta, "f%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-crf", "18", "-movflags", "+faststart", salida,
    ], check=True)
    print("ok", salida)
