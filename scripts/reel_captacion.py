"""Reel vertical 1080x1920 de captacion de publicantes para Buenas Raices Formosa.

Genera los frames con PIL y los arma en mp4 con ffmpeg. El cuerpo es motion
graphics sobre la identidad de la marca (verde, dorado, Inter), asi que el
resultado es consistente con las placas del feed.

Uso:  python3 -I scripts/reel_captacion.py <carpeta_frames> <salida.mp4>
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pieza_propiedad import (GREEN, GREEN_D, GOLD, WHITE,
                             f_head, f_semi, f_med, f_reg,
                             logo_rgba, tracked, wrap)

W, H = 1080, 1920
FPS = 30
M = 100
SOFT = (209, 224, 215)
# Desplazamiento vertical del bloque de contenido: baja la composicion para que
# no quede todo arriba, sin invadir la franja inferior donde Instagram pone la
# UI del Reel (ultimos ~250 px).
DY = 180


# ---------------------------------------------------------------- utilidades

def ease_out(t):
    """Cubica ease-out, t en [0,1]."""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def fade_in(frame, start, dur):
    """Progreso 0..1 de una animacion que arranca en `start` y dura `dur`."""
    return ease_out((frame - start) / float(dur))


def blend(c, bg, a):
    """Mezcla color c sobre bg con alfa a (0..1)."""
    return tuple(int(bg[i] + (c[i] - bg[i]) * a) for i in range(3))


def base_bg():
    """Fondo verde con el motivo de arcos dorados, calculado una sola vez."""
    img = Image.new("RGB", (W, H), GREEN)
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(6):
        r = 820 + i * 150
        cy = H + 300
        bd.arc([W // 2 - r, cy - r // 2, W // 2 + r, cy + r // 2],
               start=185, end=355, fill=GOLD + (28,), width=15)
    return Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")


def draw_marca(d, img, alpha=1.0):
    """Logo + wordmark en la cabecera."""
    lg = logo_rgba()
    lh = 112
    lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
    if alpha < 1.0:
        lg = lg.copy()
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(lg, (M, 120), lg)
    wx = M + lg.width + 28
    d.text((wx, 140), "BUENAS RAÍCES", font=f_semi(31),
           fill=blend(WHITE, GREEN, alpha))
    tracked(d, (wx + 2, 181), "F O R M O S A", f_med(23),
            blend(GOLD, GREEN, alpha), track=1.4)


def texto_animado(d, lineas, font, y0, lh, prog, fill, dy=46, x=M):
    """Dibuja lineas con fade + desplazamiento vertical."""
    a = prog
    if a <= 0:
        return y0 + lh * len(lineas)
    off = int(dy * (1 - a))
    y = y0 + off
    for ln in lineas:
        d.text((x, y), ln, font=font, fill=blend(fill, GREEN, a))
        y += lh
    return y0 + lh * len(lineas)


def tarjeta(d, y, num, titulo, prog):
    """Tarjeta numerada de un paso, con fade + slide lateral."""
    if prog <= 0:
        return
    a = prog
    dx = int(60 * (1 - a))
    x0, x1 = M + dx, W - M + dx
    alto = 152
    d.rounded_rectangle([x0, y, x1, y + alto], radius=22,
                        fill=blend(GREEN_D, GREEN, a))
    d.ellipse([x0 + 38, y + 50, x0 + 90, y + 102], fill=blend(GOLD, GREEN, a))
    nf = f_head(30)
    nw = d.textlength(num, font=nf)
    d.text((x0 + 64 - nw / 2, y + 60), num, font=nf, fill=blend(GREEN, GOLD, a))
    tf = f_semi(40)
    tl = wrap(d, titulo, tf, x1 - x0 - 150)[:2]
    ty = y + (alto - len(tl) * 48) / 2
    for ln in tl:
        d.text((x0 + 122, ty), ln, font=tf, fill=blend(WHITE, GREEN, a))
        ty += 48


def boton(d, y, prog):
    """Boton dorado del cierre."""
    if prog <= 0:
        return
    a = prog
    alto = 124
    esc = 0.9 + 0.1 * a
    ancho = int((W - 2 * M) * esc)
    x0 = (W - ancho) // 2
    d.rounded_rectangle([x0, y, x0 + ancho, y + alto], radius=alto // 2,
                        fill=blend(GOLD, GREEN, a))
    f = f_semi(46)
    t = "buenasraicesformosa.com.ar"
    tw = d.textlength(t, font=f)
    d.text(((W - tw) / 2, y + (alto - 58) / 2), t, font=f,
           fill=blend(GREEN, GOLD, a))


# ------------------------------------------------------------------- escenas

# (inicio, duracion) en frames, a 30 fps
S1 = (0, 90)      # gancho
S2 = (90, 75)     # bajada
S3 = (165, 180)   # tres pasos
S4 = (345, 105)   # cierre
TOTAL = 450       # 15 s


def render_frame(bg, n):
    img = bg.copy()
    d = ImageDraw.Draw(img)
    draw_marca(d, img, min(1.0, fade_in(n, 0, 20)))

    # --- Escena 1: gancho -------------------------------------------------
    if n < S2[0]:
        p = fade_in(n, 10, 30)
        tracked(d, (M, 420 + DY), "PARA QUIEN PUBLICA", f_semi(27),
                blend(GOLD, GREEN, p), track=1.1)
        f = f_head(100)
        texto_animado(d, ["Publicar tu", "aviso es gratis"],
                      f, 500 + DY, 116, fade_in(n, 18, 38), WHITE)
        pl = fade_in(n, 45, 25)
        if pl > 0:
            d.rectangle([M, 760 + DY, M + int(140 * pl), 766 + DY], fill=GOLD)
        f2 = f_reg(42)
        texto_animado(d, ["En el portal de Formosa."], f2, 820 + DY, 56,
                      fade_in(n, 52, 28), SOFT)

    # --- Escena 2: bajada -------------------------------------------------
    elif n < S3[0]:
        k = n - S2[0]
        p = fade_in(k, 0, 30)
        f = f_head(88)
        texto_animado(d, ["¿Tenés una", "propiedad", "en Formosa?"],
                      f, 440 + DY, 104, p, WHITE)
        d.rectangle([M, 780 + DY, M + 140, 786 + DY], fill=GOLD)
        f2 = f_reg(42)
        texto_animado(d, wrap(d, "Tu aviso, tus fotos, tu precio.", f2,
                              W - 2 * M), f2, 840 + DY, 56,
                      fade_in(k, 25, 30), SOFT)

    # --- Escena 3: tres pasos --------------------------------------------
    elif n < S4[0]:
        k = n - S3[0]
        tracked(d, (M, 400 + DY), "CÓMO FUNCIONA", f_semi(27), GOLD, track=1.1)
        pasos = [
            ("1", "Cargás tu aviso con fotos, datos y precio"),
            ("2", "Quien se interesa te contacta directo"),
            ("3", "La visita y la operación las arreglan ustedes"),
        ]
        y = 500 + DY
        for i, (num, txt) in enumerate(pasos):
            tarjeta(d, y, num, txt, fade_in(k, i * 34, 30))
            y += 182
        f2 = f_reg(38)
        texto_animado(d, wrap(d, "No somos una inmobiliaria: no intermediamos "
                                 "ni participamos de la comunicación entre "
                                 "las partes.", f2, W - 2 * M),
                      f2, 1120 + DY, 52, fade_in(k, 120, 35), SOFT)

    # --- Escena 4: cierre -------------------------------------------------
    else:
        k = n - S4[0]
        p = fade_in(k, 0, 30)
        f = f_head(92)
        texto_animado(d, ["Publicá gratis", "tu propiedad"],
                      f, 520 + DY, 108, p, WHITE)
        d.rectangle([M, 780 + DY, M + 140, 786 + DY], fill=GOLD)
        f2 = f_reg(42)
        texto_animado(d, wrap(d, "Los avisos de Formosa, en un solo lugar.",
                              f2, W - 2 * M), f2, 840 + DY, 56,
                      fade_in(k, 20, 30), SOFT)
        boton(d, 1080 + DY, fade_in(k, 40, 35))

    return img


def main():
    carpeta = sys.argv[1]
    salida = sys.argv[2]
    os.makedirs(carpeta, exist_ok=True)
    bg = base_bg()
    for n in range(TOTAL):
        render_frame(bg, n).save(os.path.join(carpeta, "f%04d.png" % n))
        if n % 90 == 0:
            print("frame", n, flush=True)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", os.path.join(carpeta, "f%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-crf", "18", "-movflags", "+faststart", salida,
    ], check=True)
    print("ok", salida)


if __name__ == "__main__":
    main()
