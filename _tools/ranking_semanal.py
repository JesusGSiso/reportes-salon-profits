#!/usr/bin/env python3
"""Ranking semanal de agendamiento — Salon Profits. v5.

Recibe los numeros ya medidos y produce un PNG por clienta destinataria, una
imagen general para Jesus y Rossana, y resultado.json con puestos, zona y los
textos de WhatsApp. No mide nada: los numeros llegan de gestion_semanal.py.

Cambios v5 (medidos el 7 sep 2026, no estimados):
  - fondo(): degradado por columna de 1 px estirada. Salida IDENTICA byte a
    byte, 53x mas rapido (1.54 s -> 0.029 s para 13 imagenes).
  - se elimino el bloque mask/tr/ImageChopsBox del dibujo de la barra: estaba
    verificado como NO-OP (reservaba ~4 lienzos completos por barra y no
    cambiaba un solo pixel). Salida IDENTICA, 8x mas rapido en esa seccion.
  - --destinatarias: solo se renderiza PNG personal para quien de verdad lo
    recibe. Las demas se siguen midiendo y rankeando (cuentan para el ranking y
    para el record) pero no se publica una imagen con su nombre que nadie abre.
"""
import argparse, base64, hashlib, io, json, math, os, sys, urllib.request, zipfile
from PIL import Image, ImageDraw, ImageFont

VERSION = 5

LINEA = 25
BUENO = 40
MIN_LEADS = 21
W = 1080

BG_TOP, BG_BOT = (58, 42, 79), (15, 13, 20)
INK, MUT, LAV = (244, 241, 238), (157, 147, 173), (201, 184, 232)
GOLD, GOLD_D = (242, 201, 76), (26, 21, 34)
VERDE, VERDE2 = (46, 204, 138), (126, 240, 187)
ROJO, ROJO2 = (179, 38, 43), (255, 92, 97)
ROJO_TXT = (255, 122, 126)
ROW_BG, ROW_LINE = (35, 30, 44), (52, 46, 62)
ROW_BAD_BG, ROW_BAD_LINE = (46, 26, 33), (88, 40, 48)
TRACK = (44, 40, 54)

ICONOS = {1: "1f3c6", 2: "1f451", 3: "1f396"}
INTER_ZIP = "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"
ICONOS_B64 = {
    "1f3c6": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAq1BMVEVHcEz/zE3/zE3/zE3/zE3/zE3/zE3/zE3/zE3/zE3/rDP/rDP/rDP/rjX/vkL/rDP/rDP/rDP/tDr/xEf/rDP/vED/rDP/rDP/wEP/sDb/rDP/rDP/zE3/zE3/rDP/rDP/rDP/zE3/zE3/zE3/zE3/zE3/rDP/rDP/wkX/ykv/xkj/tjv/sjj/uD3BaU/BaU/BaU/BaU/BaU/BaU/BaU/BaU/BaU/BaU/BaU/Lbtl5AAAAOXRSTlMAIHCAj79g/zCvgN/////vEM///6//v0D//2CfQO8gcI9Qz5/fEDBQ////////MK//72BQv99AzyD2svjjAAACS0lEQVR4AdXWB5azOgwF4JvqDCgPMyEwkz6997r/jU0RKRbnkMjw2v8t4B5LyDIoQqPZ+tXulGs1G9ipa1Ta2KFnWP2kPaPVAIqCkFb6Ru0vWokCCwA2po19ozagjdgCSMgxNHrkSIGMXAdG75AcI4zJNTB6++SIEdUPYqClJLMAOkZvAtgsKAYlYH5Bv4JCUAZmvINsIQi5qXcQKIeYmK1aGohFGBPLqgbNiKWYEwu87izr4deI2ALZKpG1jB7Ygth8UyM7MmrHYPG6NSGxGX41jNoJGOUskBAbgZ0arS5+ZcTCzWguwE48N2RALN1kxp5NOgZLiAXujLMzz+UfOY0JxUjueU3RjHLnAJASC7zetVOwC8q5/Uq87m1TjGPspobItY3GGVhKLBF1WrCGxzSCRFsi0W109CvkXK7FVIwkJmanDnIjys3gdju06iNNkIspV8gda4/UQW5OYgfhXD5JQEdzIJuNiWRTEJG0r/99YCMsBVRwqX30WYQVG5N0eKX6MVq6wNp5RNLQlLrqlxTGbErStSlzQ0I0gpQl5Lo1JS7JFQYWO7RK1scZfHXK95mfs9PyNeSnNy3dHp56pmAPFXWNcHyGqiZXsq7qbjeDOUQNM+oP80MNbgk1ZETUvzsYDG/5EaxuLi95dWNyBKguJkeKyiwJqGxErH6TEhIW1SuTojofXxihmpAK0jqtFjJ4uX943OrpWZnz9LjLCzReH3d6g8ajwh8YdP/6qPT0jm0+HtWeFGXp/G1B99ji6VHvE1s865NeIXwDBvTA37rZqRcAAAAASUVORK5CYII=",
    "1f451": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAwFBMVEVHcEz1kQ3/zE30kAz5rzz/zE3/zE3/zEz/zE3/zE3/zE3/zE30kAz/rDPnWy70kAz0kAz0kAz/zE30kAzdLkT/zE30kAz0kAz5oyT/zE3/zE3dLkT/zE3dLkTdLkTdLkT/zE3dLkT8vD6YHOv0kAz/xEdckTuur0T3nxz4piP6ri3YiojgO0XCtkb/rDP1yEzzk0q/XrC4U7pmlTyySMSFoED2mhaZp0LjwkrTvEioN9LloHXsc0jufUn3pUueJ+FYKgbxAAAAIHRSTlMA7+8gEEAwgJ+/r2BghDCfgECPz7ogv49Qz9/vcM+PIBitsd0AAAKvSURBVHhe7ZXXctswEEVBCuyyqi3JtpKAqsW1l9T//6sQWGC9AmUOZXIyycTnSXMJHCywIMX+O7wwHvN8zMdx6O3jCUTGcc7Ej2UelPccCUVo5yHkR3sUpHDt3IU8eKeo2el03ynyydZ4f5bRplvzy1lwhqvOojNTqJqOXPSXNuHCAxB1oNR9PSyCGUSE/qiEoNFtmEPCNg9BNHq9Fj4ZTAmiaKzbk01owspFhx1ag9k4igLGeiIjUYGTiRw12SU3r6VTvKcu3xrMEhn2mBC475nEPMK12zJtQkFAgoP1eUqoqG32cCIEltRVeoergoATHExE4AuYOY5h5vGEIaRdCzH2oAl9DocMpfAYGmH2PaIzhC8LgpJ8Qf0jmb22OObww1WmpprR4uKVaDDTdCIS85aDJ+e7WIjcNse71w8EYWVEDk2DvsoGssPyQBmgv2KNGTCnookRTWg612FDf+vI+yBic4fXKKElrbbTNaRDFmPTsX89B5emTIpSpyeoqEdXeRQWKyyI8kir7zEgoA83tmiCBVE2dNGAAQk9wrmwWVkF5ccmDPBwceuoMZ3k0zVJPVskNviQsoKCbP1G2CJG1hE7mNh2eyhDUUXIH18lXPKpr0RUvyisJgrJf30lgnKi54vl8uKqnCgp0DwsFE8FqgRF3puei7uF5u75TZG3U3R2P53efjP1gAdMV9aIvKj1KU3PryG8mSrOQPSwIDztGvHjPE0Pv2jPaSpRprOpRq34vNjiKj/ieyo55Up0mCrOpeirEd1I0XJb9LI14la+zinwWYlSzc9MNDXc7xAthT3iWosOaxPVtrXaDrvG9gPx1oX8td+FjMFR/Na+lHhFAioq89JWEdHPSDUR8qdFXhWR9zeLDi4rcYCiy4rUJqp/a2w0r8Don27/R/uL+eA3t4HcDMEeM50AAAAASUVORK5CYII=",
    "1f396": "iVBORw0KGgoAAAANSUhEUgAAAEgAAABICAMAAABiM0N1AAAAhFBMVEVHcEz/rDP/rDP/rDP/rDP/rDNVrO7/rDP/rDP/rDP/rDNVrO5VrO5VrO5VrO5VrO7dLkTdLkTh6O1VrO7h6O3h6O1VrO7h6O3h6O3/rDP/2YP/03n/yGX/t0f/xWD/rzj/ukz/y2r/vVH/0XT/wFb/sj3/zm//tEL/w1tVrO7dLkTh6O0wA2ovAAAAGXRSTlMAgDDP72Dfv1AgEFBgnxAwn8/v71CAz78gncDqBAAAAbVJREFUeF7szDkawjAMBeFXqfGWdbnCg/vfD+ggnxPJLqg05RQ/KgUh+Xz3OPV5JCXAVCDvIdImiQ4JDGXqEP8KoR9yyCGHHHLIoU2HNliKOhRhKmlQgq2c7qEEc3G+huaIhopcQVLQVN7r0J7R2lqDVnS0TGdoWtDVMf4644Hehm9neBVXBjkOwjAMLVAU4Ab+hKShpe39TzhyjLBURpram3n7PMXOt3NxMwVSKExukXjU5BbRB/8tGgN9EEaPZ7jSietg9/QiuMUZAOZ4E1Vvvg8xS7WkVF0LMcY7jbWuBKYQFTCpVjfaExRRWYlWVKI5TYPeB8hEGUKyFtdxfyAUlhYI3Kfue0/LZ2cclR21YWZr+7Wo4XffTz4zi/Jz93IKGlOrIzKdyIimdktl9AtSm0kElNOVcgEsoklEkmVBc77ZRZIbJYFxlMbc1XOHTzRrGoWiQTI+P/NQ0eMYt+AI5KaiTQNpHxFp0bpKk3REjEMrleUIxCy1ydBa92yq516yal9sljj0jsUWlzd23kvUxWZftYquWv/yB5zL3/8d+T9I/5fto+9IoW64+GmbIJbQ/JHnHzqGIIVbgMLwAAAAAElFTkSuQmCC",
}


def asegurar_assets(d):
    os.makedirs(d, exist_ok=True)
    faltan = [w for w in ("Bold", "ExtraBold", "SemiBold", "Regular")
              if not os.path.exists(os.path.join(d, f"Inter-{w}.ttf"))]
    if faltan:
        try:
            data = urllib.request.urlopen(INTER_ZIP, timeout=60).read()
            z = zipfile.ZipFile(io.BytesIO(data))
            for w in faltan:
                z.extract(f"extras/ttf/Inter-{w}.ttf", d)
                os.replace(os.path.join(d, "extras", "ttf", f"Inter-{w}.ttf"),
                           os.path.join(d, f"Inter-{w}.ttf"))
        except Exception as e:
            print(f"aviso: sin Inter ({e}); uso la fuente por defecto", file=sys.stderr)
    for cod in ICONOS.values():
        p = os.path.join(d, f"{cod}.png")
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            open(p, "wb").write(base64.b64decode(ICONOS_B64[cod]))


def fuente(d, peso, tam):
    p = os.path.join(d, f"Inter-{peso}.ttf")
    if os.path.exists(p):
        return ImageFont.truetype(p, tam)
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:
        return ImageFont.load_default()


def icono(d, puesto, tam):
    p = os.path.join(d, f"{ICONOS[puesto]}.png")
    try:
        return Image.open(p).convert("RGBA").resize((tam, tam), Image.LANCZOS)
    except Exception:
        pass
    im = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([2, 2, tam - 2, tam - 2], fill=GOLD)
    return im


def tapar(pal):
    n = len(pal)
    k = math.ceil(n / 2)
    return pal[:k] + "x" * (n - k)


def nombre_tapado(nombre):
    pal = [p for p in nombre.replace("-", " ").split() if p]
    if not pal:
        return "Clienta"
    if len(pal) == 1:
        return tapar(pal[0])
    return tapar(pal[0]) + " " + tapar(pal[1])


def rankear(filas):
    rank, fuera = [], []
    for f in filas:
        leads = int(f.get("leads") or 0)
        ag = int(f.get("agendaron") or 0)
        if leads < MIN_LEADS:
            fuera.append(dict(f, motivo=f"solo {leads} leads en la ventana (minimo {MIN_LEADS})"))
            continue
        rank.append(dict(f, leads=leads, agendaron=ag, tasa=round(100 * ag / leads)))
    rank.sort(key=lambda r: (-r["tasa"], -r["agendaron"], -r["leads"], r["nombre"]))
    for i, r in enumerate(rank, 1):
        r["puesto"] = i
        r["verde"] = r["tasa"] >= LINEA
        r["premio"] = i if (i <= 3 and r["verde"]) else None
    return rank, fuera


def fondo(h):
    """Degradado vertical. Misma formula que v4; una columna de 1 px estirada.
    Verificado byte a byte contra el bucle por pixel de v4."""
    col = Image.new("RGB", (1, h), BG_BOT)
    px = col.load()
    for y in range(h):
        t = min(1.0, y / (h * 0.55))
        px[0, y] = tuple(int(BG_TOP[i] * (1 - t) + BG_BOT[i] * t) for i in range(3))
    return col.resize((W, h), Image.NEAREST)


def texto(dr, xy, s, f, fill, anchor="la"):
    dr.text(xy, s, font=f, fill=fill, anchor=anchor)


def ancho(f, s):
    return f.getlength(s)


def envolver(f, s, maxw):
    out, linea = [], ""
    for w in s.split():
        prueba = (linea + " " + w).strip()
        if ancho(f, prueba) <= maxw:
            linea = prueba
        else:
            out.append(linea)
            linea = w
    if linea:
        out.append(linea)
    return out


def dibujar(rank, etiqueta, me_slug, assets, record=None, ventana_dias=7, tapar_nombres=True):
    F = lambda p, t: fuente(assets, p, t)
    n = len(rank)
    ROW_H, GAP = 78, 10
    top_h = 300
    linea_h = 44
    foot_h = 70
    h = top_h + n * (ROW_H + GAP) + linea_h + foot_h + 40
    im = fondo(h)
    dr = ImageDraw.Draw(im)

    texto(dr, (64, 58), "SALON PROFITS  ·  RANKING SEMANAL", F("SemiBold", 19), LAV)
    tit = "Semana del " if ventana_dias == 7 else "Últimas 2 semanas · "
    tam = 54
    while tam > 30 and ancho(F("ExtraBold", tam), tit + etiqueta) > W - 128:
        tam -= 2
    f_h1 = F("ExtraBold", tam)
    yt = 92 + (54 - tam) // 2
    texto(dr, (64, yt), tit, f_h1, INK)
    texto(dr, (64 + ancho(f_h1, tit), yt), etiqueta, f_h1, GOLD)
    f_sub = F("Regular", 23)
    sub = "De cada 100 personas que te trajo la publicidad, ¿cuántas terminaron con cita agendada?"
    y = 168
    for l in envolver(f_sub, sub, 950):
        texto(dr, (64, y), l, f_sub, (189, 180, 201)); y += 32
    f_m = F("SemiBold", 20)
    lin = f"Aprobado desde {LINEA}%  ·  bueno desde {BUENO}%"
    if record and record.get("tasa"):
        lin += f"  ·  récord Salon Profits: {record['tasa']}% ({nombre_tapado(record.get('nombre',''))}, {record.get('etiqueta','')})"
    texto(dr, (64, y + 8), lin, f_m, MUT)

    y = top_h
    if n and not any(r["verde"] for r in rank):
        dr.rounded_rectangle([64, y - 14, W - 64, y + 40], 14, fill=(60, 30, 36), outline=(120, 50, 58), width=2)
        texto(dr, (W // 2, y + 13), f"COPA DESIERTA ESTA SEMANA · NADIE PASÓ EL {LINEA}%", F("Bold", 20), ROJO_TXT, "mm")
        y += 66

    f_pos, f_nom, f_pct, f_small = F("ExtraBold", 30), F("Bold", 30), F("ExtraBold", 34), F("SemiBold", 16)
    f_tag, f_delta = F("ExtraBold", 15), F("Bold", 18)
    linea_dibujada = False
    for r in rank:
        if not r["verde"] and not linea_dibujada:
            cy = y + linea_h // 2 - 4
            lab = f"LÍNEA DE APROBACIÓN · {LINEA}%"
            f_l = F("ExtraBold", 19)
            lw = ancho(f_l, lab)
            for x in range(64, W - 64, 16):
                if x < (W - lw) / 2 - 20 or x > (W + lw) / 2 + 8:
                    dr.line([x, cy, x + 8, cy], fill=ROJO2, width=3)
            texto(dr, (W // 2, cy), lab, f_l, ROJO_TXT, "mm")
            y += linea_h
            linea_dibujada = True

        es_me = (r["slug"] == me_slug)
        bg, ln = (ROW_BG, ROW_LINE) if r["verde"] else (ROW_BAD_BG, ROW_BAD_LINE)
        if r["premio"] == 1:
            bg, ln = (58, 50, 34), (150, 125, 60)
        box = [64, y, W - 64, y + ROW_H]
        dr.rounded_rectangle(box, 16, fill=bg, outline=ln, width=2)
        if es_me:
            dr.rounded_rectangle(box, 16, outline=GOLD, width=4)
            dr.rounded_rectangle([60, y - 4, W - 60, y + ROW_H + 4], 19, outline=(242, 201, 76, 90), width=2)

        cy = y + ROW_H // 2
        if r["premio"]:
            ic = icono(assets, r["premio"], 52)
            im.paste(ic, (98, cy - 26), ic)
        else:
            texto(dr, (124, cy), str(r["puesto"]), f_pos, (141, 131, 160), "mm")

        col_nom = (255, 224, 138) if r["premio"] == 1 else INK
        nom = r["nombre"] if (es_me or not tapar_nombres) else nombre_tapado(r["nombre"])
        texto(dr, (176, cy), nom, f_nom, col_nom, "lm")
        if es_me:
            x0 = 176 + ancho(f_nom, nom) + 14
            dr.rounded_rectangle([x0, cy - 15, x0 + 52, cy + 15], 8, fill=GOLD)
            texto(dr, (x0 + 26, cy), "TÚ", f_tag, GOLD_D, "mm")

        bx0, bx1 = 560, 860
        dr.rounded_rectangle([bx0, cy - 9, bx1, cy + 9], 9, fill=TRACK)
        wpx = max(18, int((bx1 - bx0) * min(r["tasa"], 100) / 100))
        c1, c2 = (VERDE, VERDE2) if r["verde"] else (ROJO, ROJO2)
        for i in range(wpx):
            t = i / max(1, wpx - 1)
            c = tuple(int(c1[k] * (1 - t) + c2[k] * t) for k in range(3))
            dr.line([bx0 + i, cy - 9, bx0 + i, cy + 9], fill=c)
        # v4 tenia aqui un bloque mask/tr/ImageChopsBox verificado como NO-OP: se elimino.

        col_p = VERDE2 if r["verde"] else ROJO_TXT
        if tapar_nombres:
            texto(dr, (W - 90, cy), f"{r['tasa']}%", f_pct, col_p, "rm")
        else:
            texto(dr, (W - 90, cy - 8), f"{r['tasa']}%", f_pct, col_p, "rm")
            texto(dr, (W - 90, cy + 22), f"{r['agendaron']} de {r['leads']}", f_small, MUT, "rm")
        ta = r.get("tasa_ant")
        if ta is not None:
            d = r["tasa"] - int(ta)
            s = ("▲" if d > 0 else "▼" if d < 0 else "=") + f" {abs(d)}"
            texto(dr, (W - 200, cy), s, f_delta, VERDE2 if d > 0 else ROJO_TXT if d < 0 else MUT, "rm")
        y += ROW_H + GAP

    texto(dr, (64, h - 34), "SALON PROFITS  ·  RANKING GENERADO AUTOMÁTICAMENTE CADA LUNES", F("SemiBold", 14), (111, 101, 128))
    return im


def pct(a, b):
    return round(100 * a / b) if b else 0


def texto_top(t, tu=False):
    ga, nv = t.get("gest_antes"), t.get("notas_voz")
    suj = "Fuiste la #1 esta semana: " if tu else "Qué hizo la #1 esta semana: "
    if ga is not None:
        s = suj + ("le escribiste" if tu else "le escribió") + f" al {pct(ga, t['leads'])}% de " + ("tus" if tu else "sus") + " leads antes de que agendaran"
        if nv is not None:
            s += " y " + ("les mandaste" if tu else "les mandó") + f" nota de voz al {pct(nv, t['leads'])}%"
        s += f". Así " + ("cerraste" if tu else "cerró") + f" con {t['tasa']}% de agendamiento."
    else:
        s = suj + ("cerraste" if tu else "cerró") + f" con {t['tasa']}% de agendamiento. Pregunta gancho y nota de voz el mismo día que escriben: lo que enseñamos en la clase de seguimiento."
    return s


def texto_me(m):
    s = f"Tu semana: te llegaron {m['leads']} personas y agendaron {m['agendaron']}."
    falta = math.ceil(LINEA * m["leads"] / 100) - m["agendaron"]
    if m["tasa"] >= BUENO:
        s += " Estás en la zona buena. Sostenlo: la semana que viene te comparamos contigo misma."
    elif m["verde"]:
        falta2 = math.ceil(BUENO * m["leads"] / 100) - m["agendaron"]
        s += f" Pasaste la línea. Con {falta2} cita{'s' if falta2 != 1 else ''} más habrías llegado al {BUENO}%."
    else:
        s += f" Con {falta} cita{'s' if falta != 1 else ''} más habrías cruzado la línea del {LINEA}%. Una nota de voz a cada lead que no respondió es el camino más corto."
    return s


def mensaje(r, rank, etiqueta, url, ventana_dias=7):
    pila = r["nombre"].split()[0] if r["nombre"].split() else "hola"
    cuando = f"de la semana del {etiqueta}" if ventana_dias == 7 else f"de las últimas 2 semanas ({etiqueta})"
    top = rank[0]
    partes = [
        f"Hola {pila}, este es el ranking de agendamiento de Salon Profits {cuando}. "
        f"Estás en el puesto {r['puesto']} de {len(rank)} con {r['tasa']}% de agendamiento ({r['agendaron']} de {r['leads']}).",
        texto_top(top, tu=(top["slug"] == r["slug"])),
        texto_me(r),
        f"Si la imagen no carga, ábrela aquí: {url}",
    ]
    return "\n\n".join(partes)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--datos", required=True)
    p.add_argument("--etiqueta", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--assets", required=True)
    p.add_argument("--record")
    p.add_argument("--ventana-dias", type=int, default=7)
    p.add_argument("--sal", default="")
    p.add_argument("--url-base", default="")
    p.add_argument("--destinatarias", default="",
                   help="slugs separados por coma que SI reciben WhatsApp. Vacio = todas.")
    a = p.parse_args()

    asegurar_assets(a.assets)
    os.makedirs(a.out, exist_ok=True)
    filas = json.load(open(a.datos))
    record = json.load(open(a.record)) if a.record and os.path.exists(a.record) else None
    rank, fuera = rankear(filas)
    dest = {s.strip() for s in a.destinatarias.split(",") if s.strip()}

    def archivo(slug):
        h = hashlib.sha256(f"{a.sal}|{slug}".encode()).hexdigest()[:8]
        return f"{slug}-{h}.png"

    salida = {"rankeadas": rank, "sin_minimo": fuera, "archivos": {}, "mensajes": {},
              "ventana_dias": a.ventana_dias, "version": VERSION, "sin_imagen": []}
    if rank:
        dibujar(rank, a.etiqueta, None, a.assets, record, a.ventana_dias, tapar_nombres=False).save(
            os.path.join(a.out, archivo("general")), optimize=True)
        salida["archivos"]["general"] = archivo("general")
        for r in rank:
            if dest and r["slug"] not in dest:
                salida["sin_imagen"].append(r["slug"])
                continue
            nombre = archivo(r["slug"])
            dibujar(rank, a.etiqueta, r["slug"], a.assets, record, a.ventana_dias).save(
                os.path.join(a.out, nombre), optimize=True)
            salida["archivos"][r["slug"]] = nombre
            salida["mensajes"][r["slug"]] = mensaje(r, rank, a.etiqueta, f"{a.url_base}/{nombre}", a.ventana_dias)
    json.dump(salida, open(os.path.join(a.out, "resultado.json"), "w"), ensure_ascii=False, indent=2)
    print(f"v{VERSION} · rankeadas {len(rank)} · sin minimo {len(fuera)} · imagenes {len(salida['archivos'])}"
          + (f" · sin imagen (no reciben) {len(salida['sin_imagen'])}" if salida["sin_imagen"] else ""))
    for r in rank:
        marca = "" if (not dest or r["slug"] in dest) else "  [no recibe]"
        print(f"  {r['puesto']:>2}. {r['nombre']:<24} {r['tasa']:>3}%  {r['agendaron']}/{r['leads']}  "
              f"{'verde' if r['verde'] else 'rojo'}{'  premio ' + str(r['premio']) if r['premio'] else ''}{marca}")
    for f in fuera:
        print(f"   -  {f['nombre']:<24} fuera: {f['motivo']}")


if __name__ == "__main__":
    main()
