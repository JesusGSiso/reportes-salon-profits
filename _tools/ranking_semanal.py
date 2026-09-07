#!/usr/bin/env python3
"""
Ranking semanal de agendamiento — Salon Profits.

Recibe los numeros ya medidos (una fila por clienta) y produce:
  - una imagen PNG por clienta rankeable, con SU nombre completo y la marca TU
    y las demas con el nombre a medias;
  - una imagen general (nadie resaltado) para Jesus y Rossana;
  - resultado.json con puestos, zona, quien se envia y quien no, y por que.

No mide nada: los numeros llegan de gestion_semanal.py. No usa navegador:
solo Pillow, asi corre en cualquier entorno.

Uso:
  ranking_semanal.py --datos ranking.json --etiqueta "1 al 7 de septiembre" \
      --out /tmp/ranking/out --assets /ruta/assets [--record record.json]

ranking.json = lista de objetos:
  {"slug": "rosa-pedre", "nombre": "Rosa Pedre", "leads": 21, "agendaron": 4,
   "tasa_ant": 15 | null, "gest_antes": 3 | null, "notas_voz": 0 | null,
   "ventana_dias": 7}
record.json (opcional) = {"tasa": 58, "nombre": "Karla Bellorin", "etiqueta": "3 al 9 ago"}

Reglas (decididas el 7 sep 2026):
  LINEA = 25   -> aprobado desde 25%. Verde arriba, rojo abajo. NO es la mitad
                  del grupo: si todas estan mal, todas salen en rojo.
  MIN_LEADS = 21 -> con menos leads en la ventana no se rankea ni se le envia.
  Copa, corona y medalla SOLO en zona verde. Sin nadie en verde: copa desierta.
  Nombres: primer nombre + primer apellido, cada palabra con su segunda mitad
  tapada con x (mitad de palabra). La destinataria ve su nombre completo + TU.
"""
import argparse, hashlib, io, json, math, os, sys, urllib.request, zipfile
from PIL import Image, ImageDraw, ImageFont

LINEA = 25
BUENO = 40
MIN_LEADS = 21
W = 1080

# --- colores -----------------------------------------------------------------
BG_TOP, BG_BOT = (58, 42, 79), (15, 13, 20)
INK, MUT, LAV = (244, 241, 238), (157, 147, 173), (201, 184, 232)
GOLD, GOLD_D = (242, 201, 76), (26, 21, 34)
VERDE, VERDE2 = (46, 204, 138), (126, 240, 187)
ROJO, ROJO2 = (179, 38, 43), (255, 92, 97)
ROJO_TXT = (255, 122, 126)
ROW_BG, ROW_LINE = (35, 30, 44), (52, 46, 62)
ROW_BAD_BG, ROW_BAD_LINE = (46, 26, 33), (88, 40, 48)
TRACK = (44, 40, 54)

ICONOS = {1: "1f3c6", 2: "1f451", 3: "1f396"}   # trofeo, corona, medalla (Twemoji)
CDN = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/{}.png"
INTER_ZIP = "https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip"


# --- assets ------------------------------------------------------------------
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
        if not os.path.exists(p):
            try:
                open(p, "wb").write(urllib.request.urlopen(CDN.format(cod), timeout=30).read())
            except Exception as e:
                print(f"aviso: sin icono {cod} ({e})", file=sys.stderr)


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
    if os.path.exists(p):
        return Image.open(p).convert("RGBA").resize((tam, tam), Image.LANCZOS)
    im = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([2, 2, tam - 2, tam - 2], fill=GOLD)
    return im


# --- nombres -----------------------------------------------------------------
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


# --- ranking -----------------------------------------------------------------
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


# --- dibujo ------------------------------------------------------------------
def fondo(h):
    im = Image.new("RGB", (W, h), BG_BOT)
    px = im.load()
    for y in range(h):
        t = min(1.0, y / (h * 0.55))
        c = tuple(int(BG_TOP[i] * (1 - t) + BG_BOT[i] * t) for i in range(3))
        for x in range(W):
            px[x, y] = c
    return im


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


def dibujar(rank, etiqueta, me_slug, assets, record=None, ventana_dias=7):
    F = lambda p, t: fuente(assets, p, t)
    n = len(rank)
    ROW_H, GAP = 78, 10
    top_h = 300
    linea_h = 44
    foot_h = 250 if me_slug else 150
    h = top_h + n * (ROW_H + GAP) + linea_h + foot_h + 40
    im = fondo(h)
    dr = ImageDraw.Draw(im)

    # cabecera
    texto(dr, (64, 58), "SALON PROFITS  ·  RANKING SEMANAL", F("SemiBold", 19), LAV)
    tit = "Semana del " if ventana_dias == 7 else "Últimas 2 semanas · "
    f_h1 = F("ExtraBold", 54)
    texto(dr, (64, 92), tit, f_h1, INK)
    texto(dr, (64 + ancho(f_h1, tit), 92), etiqueta, f_h1, GOLD)
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

    # copa desierta
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
            # linea de aprobacion
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
        # puesto / premio
        if r["premio"]:
            ic = icono(assets, r["premio"], 52)
            im.paste(ic, (98, cy - 26), ic)
        else:
            texto(dr, (124, cy), str(r["puesto"]), f_pos, (141, 131, 160), "mm")

        # nombre
        col_nom = (255, 224, 138) if r["premio"] == 1 else INK
        nom = r["nombre"] if es_me else nombre_tapado(r["nombre"])
        texto(dr, (176, cy), nom, f_nom, col_nom, "lm")
        if es_me:
            x0 = 176 + ancho(f_nom, nom) + 14
            dr.rounded_rectangle([x0, cy - 15, x0 + 52, cy + 15], 8, fill=GOLD)
            texto(dr, (x0 + 26, cy), "TÚ", f_tag, GOLD_D, "mm")

        # barra
        bx0, bx1 = 560, 860
        dr.rounded_rectangle([bx0, cy - 9, bx1, cy + 9], 9, fill=TRACK)
        wpx = max(18, int((bx1 - bx0) * min(r["tasa"], 100) / 100))
        c1, c2 = (VERDE, VERDE2) if r["verde"] else (ROJO, ROJO2)
        for i in range(wpx):
            t = i / max(1, wpx - 1)
            c = tuple(int(c1[k] * (1 - t) + c2[k] * t) for k in range(3))
            dr.line([bx0 + i, cy - 9, bx0 + i, cy + 9], fill=c)
        # tapar esquinas con la forma redondeada
        mask = Image.new("L", (W, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([bx0, cy - 9, bx0 + wpx, cy + 9], 9, fill=255)
        tr = Image.new("RGB", (W, h), TRACK)
        tr.paste(im, (0, 0), mask)
        im.paste(tr, (0, 0), ImageChopsBox(mask, bx0, cy - 9, bx1, cy + 9))
        dr = ImageDraw.Draw(im)

        # porcentaje + delta
        col_p = VERDE2 if r["verde"] else ROJO_TXT
        texto(dr, (W - 90, cy - 8), f"{r['tasa']}%", f_pct, col_p, "rm")
        texto(dr, (W - 90, cy + 22), f"{r['agendaron']} de {r['leads']}", f_small, MUT, "rm")
        ta = r.get("tasa_ant")
        if ta is not None:
            d = r["tasa"] - int(ta)
            s = ("▲" if d > 0 else "▼" if d < 0 else "=") + f" {abs(d)}"
            texto(dr, (W - 200, cy), s, f_delta, VERDE2 if d > 0 else ROJO_TXT if d < 0 else MUT, "rm")
        y += ROW_H + GAP

    # pie
    y += 18
    f_bt, f_bp = F("ExtraBold", 15), F("Regular", 21)
    top = rank[0] if rank else None
    if me_slug:
        me = next((r for r in rank if r["slug"] == me_slug), None)
        cajas = []
        if top:
            cajas.append(("QUÉ HIZO LA #1 ESTA SEMANA", caja_top(top)))
        if me:
            cajas.append(("TU SEMANA", caja_me(me)))
        cw = (W - 128 - 18) // 2 if len(cajas) == 2 else W - 128
        x = 64
        for t, p in cajas:
            dr.rounded_rectangle([x, y, x + cw, y + 170], 16, fill=(35, 30, 44), outline=(52, 46, 62), width=2)
            texto(dr, (x + 22, y + 20), t, f_bt, LAV)
            yy = y + 52
            for l in envolver(f_bp, p, cw - 44)[:4]:
                texto(dr, (x + 22, yy), l, f_bp, (238, 232, 245)); yy += 28
            x += cw + 18
        y += 190
    else:
        f_g = F("Regular", 20)
        texto(dr, (64, y), f"Versión general · {n} clientas rankeadas · sin resaltar a nadie", f_g, MUT)
        y += 60
    texto(dr, (64, h - 34), "SALON PROFITS  ·  RANKING GENERADO AUTOMÁTICAMENTE CADA LUNES", F("SemiBold", 14), (111, 101, 128))
    return im


def ImageChopsBox(mask, x0, y0, x1, y1):
    """Mascara limitada a la caja de la barra: fuera de ahi no toca nada."""
    m = Image.new("L", mask.size, 0)
    m.paste(mask.crop((x0, y0, x1 + 1, y1 + 1)), (x0, y0))
    return m


def caja_top(t):
    s = f"Agendó {t['agendaron']} de {t['leads']} leads."
    ga, nv = t.get("gest_antes"), t.get("notas_voz")
    if ga is not None:
        s += f" Le escribió a {ga} de {t['leads']} antes de que agendaran"
        s += f" y mandó nota de voz a {nv}." if nv is not None else "."
    else:
        s += " Pregunta gancho y nota de voz el mismo día que escriben: lo que enseñamos en la clase de seguimiento."
    return s


def caja_me(m):
    s = f"Te llegaron {m['leads']} personas y agendaron {m['agendaron']}."
    falta = math.ceil(LINEA * m["leads"] / 100) - m["agendaron"]
    if m["tasa"] >= BUENO:
        s += " Estás en la zona buena. Sostenlo: la semana que viene te comparamos contigo misma."
    elif m["verde"]:
        falta2 = math.ceil(BUENO * m["leads"] / 100) - m["agendaron"]
        s += f" Pasaste la línea. Con {falta2} cita{'s' if falta2 != 1 else ''} más habrías llegado al {BUENO}%."
    else:
        s += f" Con {falta} cita{'s' if falta != 1 else ''} más habrías cruzado la línea. Una nota de voz a cada lead que no respondió es el camino más corto."
    return s


# --- main --------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--datos", required=True)
    p.add_argument("--etiqueta", required=True, help='ej. "1 al 7 de septiembre"')
    p.add_argument("--out", required=True)
    p.add_argument("--assets", required=True)
    p.add_argument("--record")
    p.add_argument("--ventana-dias", type=int, default=7)
    p.add_argument("--sal", default="", help="sal para el hash del nombre de archivo (URL no adivinable)")
    a = p.parse_args()

    asegurar_assets(a.assets)
    os.makedirs(a.out, exist_ok=True)
    filas = json.load(open(a.datos))
    record = json.load(open(a.record)) if a.record and os.path.exists(a.record) else None
    rank, fuera = rankear(filas)

    def archivo(slug):
        h = hashlib.sha256(f"{a.sal}|{slug}".encode()).hexdigest()[:8]
        return f"{slug}-{h}.png"

    salida = {"rankeadas": rank, "sin_minimo": fuera, "archivos": {}, "ventana_dias": a.ventana_dias}
    if rank:
        dibujar(rank, a.etiqueta, None, a.assets, record, a.ventana_dias).save(os.path.join(a.out, archivo("general")), optimize=True)
        salida["archivos"]["general"] = archivo("general")
        for r in rank:
            nombre = archivo(r["slug"])
            dibujar(rank, a.etiqueta, r["slug"], a.assets, record, a.ventana_dias).save(os.path.join(a.out, nombre), optimize=True)
            salida["archivos"][r["slug"]] = nombre
    json.dump(salida, open(os.path.join(a.out, "resultado.json"), "w"), ensure_ascii=False, indent=2)
    print(f"rankeadas {len(rank)} · sin minimo {len(fuera)} · imagenes {len(salida['archivos'])}")
    for r in rank:
        print(f"  {r['puesto']:>2}. {r['nombre']:<24} {r['tasa']:>3}%  {r['agendaron']}/{r['leads']}  {'verde' if r['verde'] else 'rojo'}{'  premio ' + str(r['premio']) if r['premio'] else ''}")
    for f in fuera:
        print(f"   -  {f['nombre']:<24} fuera: {f['motivo']}")


if __name__ == "__main__":
    main()
