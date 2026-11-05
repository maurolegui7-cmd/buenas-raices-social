"""Reels verticales 1080x1920 para piezas de mensaje (consejos, educativo).

Mismo lenguaje visual que `pieza_mensaje.py` pero en video: etiqueta, titular,
bajada, tarjetas con viñeta dorada y cierre con boton. Reusa los helpers de
`reel_captacion.py` para que todos los Reels compartan fondo, marca y curvas
de animacion.

Uso:
    from reel_mensaje import build_reel_mensaje
    build_reel_mensaje(carpeta_frames, "salida.mp4",
                       etiqueta="ANTES DE COMPRAR",
                       titulo="Qué gastos tiene una compraventa",
                       bajada="Además del precio, la operación suma costos propios.",
                       puntos=["impuestos y sellos", "honorarios", "informes"],
                       cierre="Quién paga cada concepto se acuerda")
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pieza_propiedad import (GREEN, GREEN_D, GOLD, WHITE,
                             f_head, f_semi, f_med, f_reg, wrap)
from reel_captacion import (W, H, FPS, M, DY, SOFT,
                            fade_in, blend, base_bg, draw_marca,
                            texto_animado, boton)

# (inicio, duracion) en frames a 30 fps
S1 = (0, 90)       # etiqueta + titular
S2 = (90, 90)      # bajada
S3 = (180, 195)    # tarjetas
S4 = (375, 75)     # cierre + boton
TOTAL = 450        # 15 s


def tarjeta_punto(d, y, texto, prog, alto=140):
    """Tarjeta con viñeta dorada, al estilo de las placas de mensaje."""
    if prog <= 0:
        return
    a = prog
    dx = int(60 * (1 - a))
    x0, x1 = M + dx, W - M + dx
    d.rounded_rectangle([x0, y, x1, y + alto], radius=22,
                        fill=blend(GREEN_D, GREEN, a))
    cy = y + alto // 2
    d.ellipse([x0 + 46, cy - 11, x0 + 68, cy + 11], fill=blend(GOLD, GREEN, a))
    f = f_med(40)
    lineas = wrap(d, texto, f, x1 - x0 - 150)[:2]
    ty = cy - len(lineas) * 24
    for ln in lineas:
        d.text((x0 + 104, ty), ln, font=f, fill=blend(WHITE, GREEN, a))
        ty += 48


def render_frame(bg, n, etiqueta, titulo, bajada, puntos, cierre, tsize):
    img = bg.copy()
    d = ImageDraw.Draw(img)
    draw_marca(d, img, min(1.0, fade_in(n, 0, 20)))

    # --- Escena 1: etiqueta + titular ------------------------------------
    if n < S2[0]:
        p = fade_in(n, 10, 28)
        from reel_captacion import tracked
        tracked(d, (M, 420 + DY), etiqueta, f_semi(27),
                blend(GOLD, GREEN, p), track=1.1)
        f = f_head(tsize)
        lineas = wrap(d, titulo, f, W - 2 * M)[:3]
        texto_animado(d, lineas, f, 500 + DY, int(tsize * 1.16),
                      fade_in(n, 18, 38), WHITE)
        pl = fade_in(n, 48, 25)
        if pl > 0:
            y = 500 + DY + int(tsize * 1.16) * len(lineas) + 24
            d.rectangle([M, y, M + int(140 * pl), y + 6], fill=GOLD)

    # --- Escena 2: bajada -------------------------------------------------
    elif n < S3[0]:
        k = n - S2[0]
        f = f_reg(54)
        lineas = wrap(d, bajada, f, W - 2 * M)[:4]
        y0 = 560 + DY - (len(lineas) - 2) * 34
        texto_animado(d, lineas, f, y0, 72, fade_in(k, 0, 32), WHITE)
        pl = fade_in(k, 28, 25)
        if pl > 0:
            d.rectangle([M, y0 + 72 * len(lineas) + 30,
                         M + int(140 * pl), y0 + 72 * len(lineas) + 36],
                        fill=GOLD)

    # --- Escena 3: tarjetas ----------------------------------------------
    elif n < S4[0]:
        k = n - S3[0]
        from reel_captacion import tracked
        tracked(d, (M, 420 + DY), etiqueta, f_semi(27), GOLD, track=1.1)
        y = 520 + DY
        for i, p in enumerate(puntos[:3]):
            tarjeta_punto(d, y, p, fade_in(k, i * 32, 30))
            y += 168

    # --- Escena 4: cierre -------------------------------------------------
    else:
        k = n - S4[0]
        p = fade_in(k, 0, 28)
        if cierre:
            f = f_head(66)
            lineas = wrap(d, cierre, f, W - 2 * M)[:3]
            texto_animado(d, lineas, f, 600 + DY, 78, p, WHITE)
        f2 = f_reg(40)
        texto_animado(d, ["Los avisos de Formosa, en un solo lugar."],
                      f2, 900 + DY, 54, fade_in(k, 18, 28), SOFT)
        boton(d, 1080 + DY, fade_in(k, 30, 32))

    return img


def build_reel_mensaje(carpeta, salida, etiqueta, titulo, bajada, puntos,
                       cierre="", titulo_size=92):
    os.makedirs(carpeta, exist_ok=True)
    for f in os.listdir(carpeta):
        if f.endswith(".png"):
            os.remove(os.path.join(carpeta, f))
    bg = base_bg()
    for n in range(TOTAL):
        render_frame(bg, n, etiqueta, titulo, bajada, puntos, cierre,
                     titulo_size).save(os.path.join(carpeta, "f%04d.png" % n))
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", os.path.join(carpeta, "f%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-crf", "18", "-movflags", "+faststart", salida,
    ], check=True)
    print("ok", salida)
