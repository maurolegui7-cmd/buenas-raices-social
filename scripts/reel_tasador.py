"""Reel vertical 1080x1920 de captacion a traves del tasador.

Reemplaza al Reel de captacion directa ("publicar es gratis"): en vez de pedir
compromiso pide curiosidad, que convierte mejor como puerta de entrada. El
"publica" queda al final, que es donde el propio tasador lo ofrece.

Todo lo que afirma esta verificado contra https://buenasraicesformosa.com.ar/tasador
(06/11/2026): la estimacion es gratis, no pide registro en el primer paso, usa
avisos reales de la ciudad, y el cierre repite la advertencia de que es una
estimacion orientativa y no una tasacion profesional.

Uso:  python3 -I scripts/reel_tasador.py <carpeta_frames> <salida.mp4>
"""
import os
import subprocess
import sys

from PIL import ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pieza_propiedad import (GREEN, GREEN_D, GOLD, WHITE,
                             f_head, f_semi, f_med, f_reg, wrap)
from reel_captacion import (W, H, FPS, M, DY, SOFT,
                            fade_in, blend, base_bg, draw_marca,
                            texto_animado, tarjeta, tracked)

URL = "buenasraicesformosa.com.ar/tasador"

S1 = (0, 90)       # gancho
S2 = (90, 75)      # bajada
S3 = (165, 180)    # tres pasos
S4 = (345, 105)    # cierre + boton
TOTAL = 450        # 15 s


def boton_tasador(d, y, prog):
    """Boton dorado con la URL del tasador (mas larga que la del home)."""
    if prog <= 0:
        return
    a = prog
    alto = 124
    esc = 0.9 + 0.1 * a
    ancho = int((W - 2 * M + 40) * esc)
    x0 = (W - ancho) // 2
    d.rounded_rectangle([x0, y, x0 + ancho, y + alto], radius=alto // 2,
                        fill=blend(GOLD, GREEN, a))
    f = f_semi(40)
    tw = d.textlength(URL, font=f)
    d.text(((W - tw) / 2, y + (alto - 52) / 2), URL, font=f,
           fill=blend(GREEN, GOLD, a))


def render_frame(bg, n):
    img = bg.copy()
    d = ImageDraw.Draw(img)
    draw_marca(d, img, min(1.0, fade_in(n, 0, 20)))

    # --- Escena 1: el gancho ---------------------------------------------
    if n < S2[0]:
        p = fade_in(n, 10, 30)
        tracked(d, (M, 400 + DY), "TASADOR ONLINE", f_semi(27),
                blend(GOLD, GREEN, p), track=1.1)
        f = f_head(94)
        texto_animado(d, ["¿Cuánto vale", "tu casa", "en Formosa?"],
                      f, 480 + DY, 110, fade_in(n, 18, 38), WHITE)
        pl = fade_in(n, 50, 25)
        if pl > 0:
            d.rectangle([M, 830 + DY, M + int(140 * pl), 836 + DY], fill=GOLD)

    # --- Escena 2: la promesa --------------------------------------------
    elif n < S3[0]:
        k = n - S2[0]
        p = fade_in(k, 0, 30)
        f = f_head(80)
        texto_animado(d, ["Calculalo gratis", "y sin registrarte."],
                      f, 500 + DY, 96, p, WHITE)
        d.rectangle([M, 740 + DY, M + 140, 746 + DY], fill=GOLD)
        f2 = f_reg(42)
        texto_animado(d, wrap(d, "Con datos de avisos reales de la ciudad.",
                              f2, W - 2 * M), f2, 800 + DY, 56,
                      fade_in(k, 25, 30), SOFT)

    # --- Escena 3: los tres pasos ----------------------------------------
    elif n < S4[0]:
        k = n - S3[0]
        tracked(d, (M, 400 + DY), "CÓMO FUNCIONA", f_semi(27), GOLD, track=1.1)
        pasos = [
            ("1", "Cargás los datos de tu propiedad"),
            ("2", "Ves el valor estimado al instante"),
            ("3", "Si querés, la publicás ahí mismo"),
        ]
        y = 500 + DY
        for i, (num, txt) in enumerate(pasos):
            tarjeta(d, y, num, txt, fade_in(k, i * 34, 30))
            y += 182
        f2 = f_reg(38)
        texto_animado(d, wrap(d, "Publicar tu aviso también es gratis.", f2,
                              W - 2 * M), f2, 1120 + DY, 52,
                      fade_in(k, 120, 35), SOFT)

    # --- Escena 4: cierre -------------------------------------------------
    else:
        k = n - S4[0]
        p = fade_in(k, 0, 30)
        f = f_head(92)
        texto_animado(d, ["Tasá tu", "propiedad"], f, 500 + DY, 108, p, WHITE)
        d.rectangle([M, 760 + DY, M + 140, 766 + DY], fill=GOLD)
        f2 = f_reg(34)
        texto_animado(d, wrap(d, "Es una estimación orientativa, no una "
                                 "tasación profesional.", f2, W - 2 * M),
                      f2, 820 + DY, 46, fade_in(k, 20, 30), SOFT)
        boton_tasador(d, 1080 + DY, fade_in(k, 40, 35))

    return img


def main():
    carpeta, salida = sys.argv[1], sys.argv[2]
    os.makedirs(carpeta, exist_ok=True)
    for f in os.listdir(carpeta):
        if f.endswith(".png"):
            os.remove(os.path.join(carpeta, f))
    bg = base_bg()
    for n in range(TOTAL):
        render_frame(bg, n).save(os.path.join(carpeta, "f%04d.png" % n))
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", os.path.join(carpeta, "f%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-crf", "18", "-movflags", "+faststart", salida,
    ], check=True)
    print("ok", salida)


if __name__ == "__main__":
    main()
