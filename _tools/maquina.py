"""Genera equipo/maquina/index.html: presentación 'La máquina de clientas de alto valor'."""
import math
from html import escape as esc

OUT = "/home/claude/reportes-salon-profits/equipo/maquina/index.html"
INK = "#1A1612"
STONE = "#5C5249"
BRONZE = "#7A5C2E"
MARK = "#EBDDBF"

# ---------- primitivas de dibujo ----------

def t(x, y, s, size=32, anchor="start", weight=400, fill=INK, rot=0):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}" class="hw"{tr}>{esc(s)}</text>')

def tl(x, y, lines, size=32, anchor="start", weight=400, lh=1.15, fill=INK, first_bold=False):
    out = []
    for i, ln in enumerate(lines):
        w = 700 if (first_bold and i == 0) else weight
        out.append(t(x, y + i * size * lh, ln, size, anchor, w, fill))
    return "".join(out)

def line(x1, y1, x2, y2, w=4, col=INK, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}"{d}/>'

def path(d, w=4, fill="none", col=INK):
    return f'<path d="{d}" stroke="{col}" stroke-width="{w}" fill="{fill}"/>'

def rect(x, y, w, h, r=6, sw=4, fill="none", col=INK, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" stroke="{col}" stroke-width="{sw}" fill="{fill}"{d}/>'

def circ(x, y, r, sw=4, fill="none", col=INK):
    return f'<circle cx="{x}" cy="{y}" r="{r}" stroke="{col}" stroke-width="{sw}" fill="{fill}"/>'

def dot(x, y, r=3, col=INK):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" stroke="none"/>'

def arrow(x1, y1, x2, y2, bend=0, w=4, head=16, col=INK):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    cx, cy = mx - dy / L * bend, my + dx / L * bend
    ang = math.atan2(y2 - cy, x2 - cx)
    a1, a2 = ang + math.radians(150), ang - math.radians(150)
    h1 = (x2 + head * math.cos(a1), y2 + head * math.sin(a1))
    h2 = (x2 + head * math.cos(a2), y2 + head * math.sin(a2))
    return (path(f"M{x1},{y1} Q{cx:.1f},{cy:.1f} {x2},{y2}", w, col=col) +
            path(f"M{h1[0]:.1f},{h1[1]:.1f} L{x2},{y2} L{h2[0]:.1f},{h2[1]:.1f}", w, col=col))

def check(x, y, s=1, w=5):
    return path(f"M{x-12*s},{y} L{x-3*s},{y+10*s} L{x+14*s},{y-12*s}", w)

def cross(x, y, s=1, w=5):
    return line(x - 11 * s, y - 11 * s, x + 11 * s, y + 11 * s, w) + line(x + 11 * s, y - 11 * s, x - 11 * s, y + 11 * s, w)

def coin(x, y, r=18):
    return circ(x, y, r, 3, "#fff") + t(x, y + r * 0.42, "$", r * 1.2, "middle", 700)

def tag(x, y, label, size=30, rot=-6, fill="#fff"):
    w = len(label) * size * 0.56 + 34
    h = size * 1.45
    g = (f'<g transform="rotate({rot} {x} {y})">'
         f'<path d="M{x},{y} L{x+16},{y-h/2} L{x+w},{y-h/2} L{x+w},{y+h/2} L{x+16},{y+h/2} Z" '
         f'stroke="{INK}" stroke-width="3.5" fill="{fill}"/>'
         f'{circ(x+16, y, 4, 2.5)}'
         f'{t(x + 24 + (w-24)/2, y + size*0.34, label, size, "middle", 700)}</g>')
    return g

def bubble(x, y, w, h, lines, tail, size=30, first_bold=False, fill="#fff"):
    tx, ty = tail
    bx = min(max(tx, x + 24), x + w - 24)
    by = y + h if ty > y + h else y
    base = (f'<path d="M{bx-14},{by} L{tx},{ty} L{bx+14},{by}" stroke="{INK}" stroke-width="3.5" fill="{fill}"/>')
    body = rect(x, y, w, h, 18, 3.5, fill)
    cover = line(bx - 12, by, bx + 12, by, 6, fill)
    txt = tl(x + w / 2, y + size * 1.05 + (h - len(lines) * size * 1.15) / 2 - 2, lines, size, "middle", first_bold=first_bold)
    return body + base + cover + txt

def thought(x, y, w, h, lines, size=28):
    out = (f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" stroke="{INK}" stroke-width="3.5" fill="#fff"/>')
    out += tl(x + w / 2, y + h / 2 + size * 0.35 - (len(lines) - 1) * size * 0.58, lines, size, "middle")
    return out

def woman(x, y, s=1.0, mood="smile", spots=False, sweat=False, arms="down", hat=False, hair=True, held=None):
    """Monito mujer: (x,y) centro de la cabeza."""
    r = 20 * s
    o = []
    if hair:
        o.append(path(f"M{x-21*s},{y+30*s} Q{x-30*s},{y-28*s} {x},{y-25*s} Q{x+30*s},{y-28*s} {x+21*s},{y+30*s}", 4 * min(1, s + .2)))
    o.append(circ(x, y, r, 4 * min(1, s + .2), "#fff"))
    if hat:
        o.append(path(f"M{x-16*s},{y-17*s} L{x-16*s},{y-32*s} Q{x-30*s},{y-48*s} {x-12*s},{y-54*s} Q{x},{y-70*s} {x+12*s},{y-54*s} Q{x+30*s},{y-48*s} {x+16*s},{y-32*s} L{x+16*s},{y-17*s}", 4, "#fff"))
    o.append(dot(x - 7 * s, y - 3 * s, 2.4 * s))
    o.append(dot(x + 7 * s, y - 3 * s, 2.4 * s))
    if mood == "smile":
        o.append(path(f"M{x-8*s},{y+6*s} Q{x},{y+14*s} {x+8*s},{y+6*s}", 3 * min(1, s + .2)))
    elif mood == "sad":
        o.append(path(f"M{x-8*s},{y+12*s} Q{x},{y+5*s} {x+8*s},{y+12*s}", 3 * min(1, s + .2)))
    elif mood == "wow":
        o.append(circ(x, y + 9 * s, 3.5 * s, 2.5))
    else:
        o.append(line(x - 7 * s, y + 9 * s, x + 7 * s, y + 9 * s, 3 * min(1, s + .2)))
    if spots:
        for (a, b) in [(-11, 5), (12, 4), (-4, -12), (8, -11)]:
            o.append(dot(x + a * s, y + b * s, 2.8 * s, BRONZE))
    if sweat:
        o.append(path(f"M{x+27*s},{y-14*s} Q{x+21*s},{y-2*s} {x+27*s},{y}" f" Q{x+33*s},{y-2*s} {x+27*s},{y-14*s}", 3, "#fff"))
    sw = 4 * min(1, s + .2)
    o.append(line(x, y + r, x, y + 30 * s, sw))
    o.append(path(f"M{x},{y+30*s} L{x-27*s},{y+108*s} L{x+27*s},{y+108*s} Z", sw, "#fff"))
    o.append(line(x - 10 * s, y + 108 * s, x - 13 * s, y + 152 * s, sw))
    o.append(line(x + 10 * s, y + 108 * s, x + 13 * s, y + 152 * s, sw))
    if arms == "down":
        o.append(line(x - 5 * s, y + 42 * s, x - 30 * s, y + 82 * s, sw))
        o.append(line(x + 5 * s, y + 42 * s, x + 30 * s, y + 82 * s, sw))
    elif arms == "up":
        o.append(line(x - 5 * s, y + 42 * s, x - 34 * s, y + 6 * s, sw))
        o.append(line(x + 5 * s, y + 42 * s, x + 34 * s, y + 6 * s, sw))
    elif arms == "point":
        o.append(line(x - 5 * s, y + 42 * s, x - 30 * s, y + 82 * s, sw))
        o.append(line(x + 5 * s, y + 42 * s, x + 50 * s, y + 36 * s, sw))
    elif arms == "hold":
        o.append(line(x - 5 * s, y + 42 * s, x + 26 * s, y + 62 * s, sw))
        o.append(line(x + 5 * s, y + 42 * s, x + 34 * s, y + 56 * s, sw))
    return "".join(o)

def seated(x, y, s=1.0, mood="smile", spots=False, facing=1, arms="lap"):
    """Monito sentado; facing=1 mira a la derecha."""
    r = 20 * s
    f = facing
    o = [path(f"M{x-21*s},{y+30*s} Q{x-30*s},{y-28*s} {x},{y-25*s} Q{x+30*s},{y-28*s} {x+21*s},{y+30*s}", 4),
         circ(x, y, r, 4, "#fff"), dot(x + f * 4 * s, y - 3 * s, 2.4 * s), dot(x + f * 13 * s, y - 3 * s, 2.4 * s)]
    if mood == "smile":
        o.append(path(f"M{x+f*1*s},{y+7*s} Q{x+f*8*s},{y+14*s} {x+f*15*s},{y+6*s}", 3))
    else:
        o.append(line(x + f * 2 * s, y + 9 * s, x + f * 14 * s, y + 9 * s, 3))
    if spots:
        for (a, b) in [(-8, 6), (10, 8), (2, -12)]:
            o.append(dot(x + a * s, y + b * s, 2.8 * s, BRONZE))
    o.append(line(x, y + r, x, y + 80 * s, 4))
    o.append(path(f"M{x},{y+80*s} L{x+f*45*s},{y+80*s} L{x+f*45*s},{y+125*s}", 4))
    if arms == "lap":
        o.append(path(f"M{x},{y+40*s} L{x+f*20*s},{y+62*s} L{x+f*40*s},{y+70*s}", 4))
    elif arms == "hold":
        o.append(path(f"M{x},{y+40*s} L{x+f*28*s},{y+52*s} L{x+f*48*s},{y+40*s}", 4))
    # silla
    o.append(path(f"M{x-f*14*s},{y+30*s} L{x-f*14*s},{y+92*s} L{x+f*40*s},{y+92*s} M{x-f*10*s},{y+92*s} L{x-f*10*s},{y+132*s} M{x+f*36*s},{y+92*s} L{x+f*36*s},{y+132*s}", 3, col=STONE))
    return "".join(o)

def phone(x, y, w, h):
    return (rect(x, y, w, h, 26, 4, "#fff") + line(x + w / 2 - 22, y + 18, x + w / 2 + 22, y + 18, 4) +
            line(x + w / 2 - 26, y + h - 16, x + w / 2 + 26, y + h - 16, 4))

def gear(x, y, r):
    o = [circ(x, y, r, 4, "#fff"), circ(x, y, r * 0.35, 4)]
    for k in range(8):
        a = k * math.pi / 4
        o.append(line(x + r * math.cos(a), y + r * math.sin(a), x + (r + 10) * math.cos(a), y + (r + 10) * math.sin(a), 7))
    return "".join(o)

def gauge(x, y, r, val, label, size=28):
    o = [path(f"M{x-r},{y} A{r},{r} 0 0 1 {x+r},{y}", 4)]
    for k in range(5):
        a = math.pi + k * math.pi / 4
        o.append(line(x + (r - 12) * math.cos(a), y + (r - 12) * math.sin(a), x + r * math.cos(a), y + r * math.sin(a), 3))
    a = math.pi + val * math.pi
    o.append(line(x, y, x + (r - 18) * math.cos(a), y + (r - 18) * math.sin(a), 5))
    o.append(dot(x, y, 7))
    o.append(line(x - r - 6, y, x + r + 6, y, 4))
    o.append(t(x, y + size + 12, label, size, "middle", 700))
    return "".join(o)

def svg(vb, shapes, texts):
    w, h = vb
    return (f'<svg viewBox="0 0 {w} {h}" role="img" xmlns="http://www.w3.org/2000/svg" '
            f'stroke-linecap="round" stroke-linejoin="round">'
            f'<g filter="url(#rough)">{shapes}</g>{texts}</svg>')

# ---------- dibujos por lámina ----------

def d_portada():
    S, T = [], []
    # tolva
    S.append(path("M150,70 L330,70 L280,150 L200,150 Z", 4, "#fff"))
    S += [coin(205, 38, 17), coin(255, 22, 17), coin(300, 44, 17)]
    T.append(t(240, 108, "anuncios", 28, "middle", 700))
    # cuerpo
    S.append(rect(100, 150, 520, 270, 14, 4, "#fff"))
    S.append(gear(175, 360, 30)); S.append(gear(545, 360, 30))
    T.append(tl(360, 210, ["dolor → puerta →", "vitrina → consulta", "→ sala"], 34, "middle", 700))
    # salida
    S.append(path("M620,300 L700,300 L700,350 L620,350", 4, "#fff"))
    S.append(arrow(705, 325, 745, 325, 0, 4, 14))
    S += [woman(790, 250, .62, "smile"), woman(850, 270, .55, "smile")]
    T.append(tl(812, 400, ["clientas", "de alto valor"], 28, "middle", 700))
    T.append(t(812, 470, "$$$", 44, "middle", 700, BRONZE))
    return svg((900, 500), "".join(S), "".join(T))

def d_mismo_dinero():
    S, T = [], []
    for row in range(5):
        for col in range(6):
            S.append(woman(70 + col * 62, 40 + row * 62, .30, "flat", hair=True))
    T.append(t(230, 395, "30 cortes de $50", 34, "middle", 700))
    T.append(t(230, 445, "= $1,500", 44, "middle", 700))
    T.append(tl(230, 490, ["30 que agendar, que lleguen", "y que no cancelen"], 26, "middle", fill=STONE))
    S.append(line(445, 175, 495, 175, 7)); S.append(line(445, 200, 495, 200, 7))
    for i, x in enumerate([590, 700, 810]):
        S.append(woman(x, 120, .85, "smile"))
    S.append(tag(600, 70, "$500", 28, -8))
    T.append(t(700, 395, "3 balayages de $500", 34, "middle", 700))
    T.append(t(700, 445, "= $1,500", 44, "middle", 700))
    T.append(t(700, 490, "3 que atender", 26, "middle", fill=STONE))
    return svg((900, 530), "".join(S), "".join(T))

def d_dolor():
    S, T = [], []
    # izquierda: ganas
    S.append(woman(180, 200, 1.0, "smile"))
    S.append(bubble(40, 40, 250, 80, ["quiero un facial"], (165, 170), 30))
    S.append(tag(240, 300, "$120", 30, -6))
    S.append(arrow(245, 362, 320, 362, -8))
    T.append(t(328, 372, "y se va", 28))
    T.append(t(180, 410, "tiene ganas", 30, "middle", 700, STONE))
    # divisor
    S.append(line(450, 40, 450, 470, 3, STONE, "8 12"))
    # derecha: dolor
    S.append(woman(640, 200, 1.0, "sad", spots=True, sweat=True))
    S.append(bubble(520, 40, 280, 80, ["ya probé de todo"], (630, 170), 30))
    S.append(tag(700, 300, "$1,500", 30, -6))
    T.append(t(640, 410, "tiene un dolor", 30, "middle", 700, STONE))
    T.append(t(735, 255, "manchas", 26, "start", 400, BRONZE))
    S.append(arrow(730, 248, 662, 205, 8, 3, 11, BRONZE))
    T.append(tl(640, 450, ["paga un programa"], 26, "middle", fill=STONE))
    return svg((900, 480), "".join(S), "".join(T))

def d_buffet():
    S, T = [], []
    # buffet
    S.append(rect(30, 270, 380, 26, 4, 4, "#fff"))
    S.append(line(60, 296, 60, 380, 4)); S.append(line(380, 296, 380, 380, 4))
    for i, lab in enumerate(["china", "italiana", "hot dogs", "marroquí"]):
        px = 75 + i * 92
        S.append(f'<ellipse cx="{px}" cy="262" rx="38" ry="10" stroke="{INK}" stroke-width="3.5" fill="#fff"/>')
        S.append(line(px + 20, 255, px + 20, 205, 3))
        S.append(path(f"M{px+20},205 L{px+48},214 L{px+20},223", 3, "#fff"))
        T.append(t(px, 192 - (i % 2) * 30, lab, 24, "middle"))
    S.append(rect(150, 40, 150, 70, 8, 4, "#fff"))
    T.append(t(225, 88, "BUFFET $", 30, "middle", 700))
    S.append(woman(495, 262, .62, "flat"))
    S.append(thought(405, 120, 185, 82, ["¿será buena", "la marroquí?"], 24))
    T.append(t(220, 445, "hace de todo = barato", 30, "middle", 700, STONE))
    # restaurante especializado
    S.append(rect(600, 130, 270, 250, 6, 4, "#fff"))
    S.append(path("M590,130 L880,130 L870,95 L600,95 Z", 4, "#fff"))
    for k in range(9):
        S.append(path(f"M{600+k*30},130 Q{615+k*30},152 {630+k*30},130", 3))
    T.append(t(735, 122, "Cocina marroquí", 26, "middle", 700))
    S.append(rect(700, 250, 70, 130, 4, 4, "#fff"))
    S.append(woman(735, 215, .55, "smile", hat=True))
    T.append(t(735, 48, "$$$", 44, "middle", 700, BRONZE))
    T.append(tl(650, 318, ["la", "dueña"], 24, "middle", 700, fill=STONE))
    T.append(t(735, 440, "especialista = caro", 30, "middle", 700, STONE))
    return svg((900, 510), "".join(S), "".join(T))

def d_dos_ofertas():
    S, T = [], []
    S.append(path("M90,120 L470,40 L850,120", 4))
    S.append(rect(110, 120, 720, 300, 4, 4, "#fff"))
    # puerta
    S.append(rect(180, 260, 110, 160, 4, 4, "#fff"))
    S.append(dot(272, 345, 5))
    S.append(rect(130, 150, 230, 90, 8, 4, MARK))
    T.append(tl(245, 186, ["¿Tienes manchas?", "Escáner GRATIS"], 28, "middle", first_bold=True))
    S.append(woman(55, 290, .62, "sad", spots=True))
    S.append(arrow(90, 400, 170, 400, -8))
    # sala
    S.append(rect(440, 150, 360, 250, 6, 3, "#fff", STONE, "10 8"))
    S.append(rect(500, 300, 240, 60, 4, 4, "#fff"))
    S.append(rect(470, 175, 300, 100, 8, 4, MARK))
    T.append(tl(620, 212, ["Programa Piel", "Sin Manchas $1,500"], 28, "middle", first_bold=True))
    S.append(arrow(300, 330, 430, 330, -14))
    T.append(t(365, 305, "diagnóstico", 22, "middle", 400, STONE))
    T.append(tl(235, 460, ["PUERTA", "front end: oferta de atracción"], 26, "middle", first_bold=True))
    T.append(tl(620, 460, ["SALA", "back end: oferta irresistible"], 26, "middle", first_bold=True))
    return svg((900, 510), "".join(S), "".join(T))

def d_anuncio():
    S, T = [], []
    S.append(phone(330, 20, 240, 470))
    S.append(rect(350, 60, 200, 300, 10, 3, "#fff"))
    S.append(woman(450, 150, .9, "sad", spots=True, hair=True))
    S.append(path("M432,320 L432,350 L462,335 Z", 3, INK))
    T.append(tl(450, 400, ["video de ella,", "la especialista"], 24, "middle", fill=STONE))
    S.append(bubble(20, 30, 280, 160, ["1. Llama", "¿Mujer en Dallas", "con manchas que", "no se van?"], (350, 110), 28, True))
    S.append(bubble(610, 140, 280, 190, ["2. Promete", "Te digo qué las", "causa y cómo", "quitarlas. Soy", "especialista."], (555, 210), 28, True))
    S.append(bubble(20, 320, 280, 125, ["3. Invita", "Agenda tu escáner", "gratis aquí"], (350, 380), 28, True))
    return svg((900, 500), "".join(S), "".join(T))

def d_oferta():
    S, T = [], []
    # izquierda: facial comparable
    for i, (lab, p) in enumerate([("facial", "$120"), ("facial", "$99"), ("facial", "$110")]):
        x = 30 + i * 140
        S.append(rect(x, 110, 125, 105, 8, 4, "#fff"))
        T.append(tl(x + 62, 152, [lab, p], 32, "middle", first_bold=False))
    S.append(woman(150, 300, .8, "flat"))
    S.append(thought(230, 270, 210, 90, ["¿cuál es", "más barato?"], 28))
    T.append(t(225, 490, "se compara por precio", 30, "middle", 700, STONE))
    S.append(line(470, 40, 470, 480, 3, STONE, "8 12"))
    # derecha: torre de soluciones
    blocks = ["escáner de control", "3 sesiones", "crema para casa", "protector solar", "seguimiento por WhatsApp"]
    for i, b in enumerate(blocks):
        y = 400 - i * 58
        S.append(rect(540, y, 300, 52, 6, 4, "#fff"))
        T.append(t(690, y + 35, b, 25, "middle"))
    S.append(path("M520,150 L860,150 L850,110 L860,70 L520,70 L530,110 Z", 4, MARK))
    T.append(tl(690, 102, ["Programa Piel Sin Manchas", "90 días · $1,500"], 25, "middle", first_bold=True))
    T.append(t(690, 490, "no se puede comparar", 30, "middle", 700, STONE))
    return svg((900, 510), "".join(S), "".join(T))

def d_precio():
    S, T = [], []
    steps = [("$250", 60, 130), ("$220", 150, 200), ("$210", 240, 270), ("$190", 330, 340)]
    d = "M30,130"
    for _, x, y in steps:
        d += f" L{x+90},{y} L{x+90},{y+70}" if False else ""
    d = "M40,130 L130,130 L130,200 L220,200 L220,270 L310,270 L310,340 L400,340 L400,420"
    S.append(path(d, 4))
    for lab, x, y in [("$250", 85, 130), ("$220", 175, 200), ("$210", 265, 270), ("$190", 355, 340)]:
        T.append(t(x, y + 40, lab, 30, "middle", 700))
    S.append(woman(85, 62, .45, "sad", arms="point"))
    S.append(woman(265, 202, .45, "sad", arms="point"))
    T.append(tl(220, 440, ["nadie sale bien", "de ese juego"], 28, "middle", 700, fill=STONE))
    S.append(line(470, 40, 470, 480, 3, STONE, "8 12"))
    # derecha: precio alto con fila
    S.append(woman(570, 110, .8, "smile"))
    S.append(tag(625, 90, "$550", 32, -8))
    S += [woman(720, 145, .55, "smile"), woman(785, 150, .5, "smile"), woman(845, 155, .45, "smile")]
    T.append(tl(700, 280, ["micropigmentadora", "con consulta"], 28, "middle", 700, fill=STONE))
    S.append(rect(530, 375, 150, 70, 6, 4, "#fff"))
    T.append(tl(605, 403, ["balayage", "$200"], 24, "middle", first_bold=True))
    S.append(thought(700, 370, 190, 80, ["¿qué tendrá", "de malo?"], 24))
    return svg((900, 500), "".join(S), "".join(T))

def d_vitrina():
    S, T = [], []
    # teléfono revuelto
    S.append(phone(110, 20, 220, 400))
    S.append(circ(160, 80, 22, 3, "#fff")); T.append(t(160, 87, "logo", 18, "middle", 700))
    labs = ["-20%", "uñas", "flyer", "pestañas", "promo", "cejas", "-30%", "láser", "?"]
    for i, lb in enumerate(labs):
        cx, cy = 130 + (i % 3) * 62, 125 + (i // 3) * 62
        S.append(rect(cx, cy, 56, 56, 4, 3, "#fff"))
        T.append(t(cx + 28, cy + 35, lb, 17, "middle"))
    S.append(cross(220, 0 + 455, 1.1))
    S.append(woman(40, 300, .5, "flat"))
    S.append(thought(0, 160, 120, 70, ["¿estafa?"], 22))
    # teléfono especializado
    S.append(phone(560, 20, 220, 400))
    S.append(circ(610, 80, 22, 3, "#fff")); S.append(woman(610, 78, .32, "smile", hair=True))
    for i in range(16):
        cx, cy = 578 + (i % 4) * 47, 118 + (i // 4) * 62
        S.append(rect(cx, cy, 42, 56, 4, 3, "#fff"))
        S.append(circ(cx + 21, cy + 22, 8, 2.5))
        S.append(path(f"M{cx+10},{cy+48} Q{cx+21},{cy+36} {cx+32},{cy+48}", 2.5))
    S.append(check(670, 455, 1.2))
    S.append(woman(845, 300, .5, "smile"))
    S.append(thought(780, 150, 120, 80, ["¡experta!"], 22))
    T.append(tl(450, 210, ["en 5", "segundos"], 30, "middle", 700, fill=STONE))
    S.append(arrow(400, 260, 500, 260, -10))
    T.append(t(220, 495, "logo y de todo", 26, "middle", 700, STONE))
    T.append(t(670, 495, "16 de lo mismo, con su cara", 26, "middle", 700, STONE))
    return svg((900, 510), "".join(S), "".join(T))

def d_consulta():
    S, T = [], []
    S.append(seated(110, 170, 1.0, "smile", facing=1, arms="hold"))
    S.append(rect(150, 175, 80, 60, 6, 4, "#fff"))
    S.append(circ(190, 202, 14, 3)); S += [dot(184, 200, 2.5, BRONZE), dot(196, 206, 2.5, BRONZE)]
    S.append(seated(330, 170, 1.0, "smile", spots=True, facing=-1))
    T.append(t(110, 370, "la dueña", 26, "middle", 700, STONE))
    T.append(t(330, 370, "la clienta", 26, "middle", 700, STONE))
    S.append(bubble(150, 50, 230, 70, ["esto es melasma"], (200, 170), 26))
    steps = ["1. ¿Qué te trajo?", "2. Muéstrale su problema", "3. ¿Qué ya probaste?", "4. Cómo va a quedar",
             "5. Ofrece la que le encaja", "6. Precio, pago y agenda"]
    for i, sline in enumerate(steps):
        T.append(t(470, 80 + i * 62, sline, 30, "start", 700 if i in (1, 4) else 400))
    S.append(line(450, 50, 450, 420, 3, STONE, "8 12"))
    return svg((900, 440), "".join(S), "".join(T))

def d_escalera():
    S, T = [], []
    d = "M40,440 L40,370 L240,370 L240,290 L440,290 L440,210 L640,210 L640,130 L860,130 L860,440"
    S.append(path(d, 4))
    items = [(140, 370, "Puerta", "escáner gratis"), (340, 290, "Sala", "programa $1,500"),
             (540, 210, "Siguiente", "manos y pies"), (750, 130, "Cada mes", "mantenimiento")]
    for x, y, a, b in items:
        T.append(tl(x, y + 34, [a, b], 26, "middle", first_bold=True))
    S.append(woman(740, 45, .45, "smile", arms="up"))
    S.append(arrow(360, 380, 330, 455, 0, 3, 12, STONE))
    T.append(t(345, 488, "¿no puede hoy? plan de pagos", 24, "start", 400, STONE))
    S.append(arrow(130, 300, 640, 70, -60, 3, 14, BRONZE))
    return svg((900, 500), "".join(S), "".join(T))

def d_maquina():
    S, T = [], []
    S.append(coin(70, 160, 30)); T.append(tl(70, 230, ["pago $100", "por clienta"], 26, "middle", 700))
    S.append(arrow(110, 160, 170, 160, 0))
    S.append(rect(180, 70, 520, 220, 14, 4, "#fff"))
    for i, lab in enumerate(["mensajes", "agendan", "llegan", "compran"]):
        S.append(gauge_mini(250 + i * 127, 170, 40))
        T.append(t(250 + i * 127, 235, lab, 24, "middle", 700))
    S.append(arrow(700, 160, 760, 160, 0))
    S.append(coin(800, 140, 22)); S.append(coin(840, 170, 22)); S.append(coin(805, 195, 22))
    T.append(tl(820, 250, ["me deja", "$1,500"], 26, "middle", 700))
    S.append(arrow(820, 300, 70, 300, -70, 4, 16, BRONZE))
    T.append(t(445, 410, "lo vuelvo a meter en anuncios", 28, "middle", 700, BRONZE))
    return svg((900, 450), "".join(S), "".join(T))

def gauge_mini(x, y, r):
    o = [path(f"M{x-r},{y} A{r},{r} 0 0 1 {x+r},{y}", 4), line(x, y, x + r * .5, y - r * .7, 4), dot(x, y, 5),
         line(x - r - 4, y, x + r + 4, y, 4)]
    return "".join(o)

def d_tablero():
    S, T = [], []
    S.append(rect(20, 20, 860, 230, 30, 4, "#fff"))
    vals = [(0.75, "mensajes"), (0.62, "citas"), (0.15, "llegan"), (0.55, "compran")]
    for i, (v, lab) in enumerate(vals):
        S.append(gauge(130 + i * 213, 165, 80, v, lab))
    S.append(circ(557, 62, 20, 4, MARK)); T.append(t(557, 73, "!", 30, "middle", 700))
    fixes = [["anuncio", "y puerta"], ["bot y", "seguimiento"], ["recordatorios", "y calentamiento"], ["consulta,", "oferta, precio"]]
    for i, f in enumerate(fixes):
        T.append(tl(130 + i * 213, 320, f, 28, "middle"))
        S.append(arrow(130 + i * 213, 258, 130 + i * 213, 288, 0, 3, 10, STONE))
    T.append(t(450, 412, "si la aguja cae, ahí está la falla", 28, "middle", 700, STONE))
    return svg((900, 430), "".join(S), "".join(T))

# ---------- tira del ejemplo completo ----------

def mini(kind):
    S, T = [], []
    if kind == 1:
        S.append(woman(70, 55, .55, "flat")); S.append(tag(110, 50, "$120", 22, -6))
        T.append(t(150, 150, "$4,000/mes", 20, "middle", 700, STONE))
    elif kind == 2:
        S.append(woman(100, 50, .6, "sad", spots=True, sweat=True))
    elif kind == 3:
        S.append(rect(30, 30, 140, 70, 8, 3, MARK)); T.append(tl(100, 60, ["escáner", "GRATIS"], 20, "middle", first_bold=True))
        S.append(rect(70, 100, 60, 60, 3, 3, "#fff"))
    elif kind == 4:
        S.append(phone(60, 10, 80, 150))
        for i in range(9):
            S.append(rect(72 + (i % 3) * 20, 40 + (i // 3) * 24, 16, 20, 2, 2, "#fff"))
    elif kind == 5:
        S.append(seated(55, 60, .6, "smile", facing=1, arms="hold")); S.append(seated(145, 60, .6, "smile", spots=True, facing=-1))
        S.append(rect(78, 62, 36, 28, 3, 3, "#fff"))
    elif kind == 6:
        S.append(woman(100, 45, .6, "smile", arms="up")); T.append(t(100, 165, "$1,500", 26, "middle", 700, BRONZE))
    return svg((200, 175), "".join(S), "".join(T))

STRIP = [
    (1, "Esteticista en Dallas", "Vende faciales de $120 y factura $4,000 al mes."),
    (2, "El dolor", "Sus clientas con manchas pagan lo que sea por quitarlas."),
    (3, "La puerta", "Anuncio: ¿manchas que no se van? Escáner facial gratis."),
    (4, "La vitrina", "16 publicaciones de manchas, con su cara."),
    (5, "La consulta", "El escáner le muestra su melasma y ella le explica el plan."),
    (6, "La sala", "Programa Piel Sin Manchas de $1,500. Con 7 al mes: $10,500."),
]

# ---------- contenido de las láminas ----------

SLIDES = [
    dict(title="La máquina de clientas de alto valor",
         sub="Cómo le damos el éxito a cada clienta de Salon Profits, en 14 dibujos.",
         fig=d_portada(), rule="No le traemos clientas. Le traemos dinero.",
         hz=None, cls="cover"),
    dict(title="Mismo dinero, 10 veces menos gente",
         fig=d_mismo_dinero(), rule="Con lo barato no se llega a la meta.",
         hz="En Hormozi: deja de ser un commodity. Si te ven igual a las demás, solo compiten por precio."),
    dict(title="1. Vende un dolor, no un servicio",
         fig=d_dolor(),
         checks=["Duele y se ve", "Pueden pagar $450 o más", "Están a 8 km de ella", "Se vende todo el año", "La buscan a ella, no a la máquina"],
         checks_title="El servicio ancla tiene que pasar las 5:",
         rule="La gente no paga por servicios. Paga por quitarse un dolor.",
         hz="En Hormozi: el mercado hambriento (Starving Crowd): dolor, dinero para pagar y fácil de encontrar."),
    dict(title="Especialista, no buffet",
         fig=d_buffet(),
         note="¿Y sus otros servicios? Se los vende después, a la clienta que ya ganó. Mira la lámina 11.",
         rule="Hacer de todo te posiciona como nada.",
         hz="En Hormozi: diferénciate. Lo que no se distingue se compra por precio."),
    dict(title="2. Las dos ofertas: la puerta y la sala",
         fig=d_dos_ofertas(),
         table=[("Esteticista", "Escáner facial gratis", "Programa de manchas, $1,500"),
                ("Colorista", "Prueba de mechón", "Transformación rubia o morena iluminada, desde $550"),
                ("Micropigmentadora", "Consulta gratis", "Transformación de cejas, $550 a $650"),
                ("Clínica", "Evaluación con las doctoras", "Programa de rejuvenecimiento íntimo, $2,500")],
         rule="Afuera atraes con el problema. Adentro vendes la solución.",
         hz="En Hormozi: el imán que revela el problema ($100M Leads) lleva a la oferta principal ($100M Money Models)."),
    dict(title="El anuncio: llama, promete, invita",
         fig=d_anuncio(),
         notes=["En el texto del anuncio, la invitación va primero.",
                "Di para quién es y para quién no: la IA de Meta lo lee.",
                "Sal con 6 a 8 anuncios distintos; siempre hay uno que gana."],
         rule="Si no dice a quién le habla, no le habla a nadie.",
         hz="En Hormozi: Callout, Value, Call to Action."),
    dict(title="3. La sala: la oferta irresistible",
         fig=d_oferta(),
         notes=["Cómo se arma: su sueño → sus miedos → una solución para cada miedo → un nombre.",
                "No le digas paquete. Dile transformación."],
         rule="No es descuento. Es tanto valor que no se puede comparar.",
         hz="En Hormozi: Grand Slam Offer. Sube el resultado y la seguridad; baja el tiempo y el esfuerzo."),
    dict(title="El precio habla",
         fig=d_precio(),
         notes=["Si dice «está caro»: plan de pagos o menos sesiones. Nunca lo mismo más barato."],
         rule="Nunca publicar precios ni descuentos.",
         hz="En Hormozi: el downsell cambia el pago o el alcance, no el valor."),
    dict(title="La vitrina: 16 publicaciones con su cara",
         fig=d_vitrina(),
         notes=["El contenido no vende solo: la publicidad trae, la vitrina convence.",
                "El logo solo no vale. Nike sin Jordan es otra cosa."],
         rule="Como te ven, te pagan.",
         hz="En Hormozi: el contenido es la prueba que sube la seguridad de lograrlo."),
    dict(title="La consulta es la venta",
         fig=d_consulta(),
         notes=["Ejemplo: una micropigmentadora cobra $550 cuando la de al lado cobra $250. En la consulta ya no la comparan."],
         rule="Afuera comparan precio. En la consulta compran confianza.",
         hz="En Hormozi: recomienda lo que necesita y dile lo que no necesita. Eso es asesorar, no presionar."),
    dict(title="Lo demás se vende adentro",
         fig=d_escalera(),
         notes=["La que se hace balayage también tiene manos y pies.",
                "A la de micropigmentación, después, la suscripción de pestañas."],
         rule="Entra por la puerta grande. Lo demás se vende adentro.",
         hz="En Hormozi: atracción, upsell, downsell y continuidad, en ese orden."),
    dict(title="La máquina y sus números",
         fig=d_maquina(),
         notes=["4 transformaciones de $2,500 = $10,000 al mes.",
                "Contestar no es vender: el dinero está en el seguimiento (el bot, 24 horas)."],
         rule="Si funciona, no lo cambies: échale más gasolina.",
         hz="En Hormozi: lo que deja la clienta en su primer mes paga lo que costó conseguirla."),
    dict(title="Todo junto: un ejemplo",
         strip=True,
         rule="Un dolor, una puerta, una sala. Y la máquina andando.",
         hz="Ejemplo para afinar juntos en la siguiente fase."),
    dict(title="El tablero de la account",
         fig=d_tablero(),
         brakes=["Publicar precios", "Hacer descuentos", "Volver a vender de todo", "Apagar la pauta cuando está lento", "Cambiar lo que funciona"],
         rule="Arregla una aguja a la vez.",
         hz="En Hormozi: More, Better, New. Primero se arregla el cuello de botella."),
]

# ---------- HTML ----------

CSS = """
@font-face{font-family:Archivo;src:url(fonts/archivo.woff2) format('woff2');font-weight:100 900;font-stretch:62% 125%;font-display:swap}
@font-face{font-family:Kalam;src:url(fonts/kalam-400.woff2) format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:Kalam;src:url(fonts/kalam-700.woff2) format('woff2');font-weight:700;font-display:swap}
:root{--papel:#FFFFFF;--tinta:#1A1612;--piedra:#5C5249;--bronce:#7A5C2E;--marca:#EBDDBF;--linea:#E4D9CA}
*{box-sizing:border-box}
html{background:var(--papel)}
body{margin:0;color:var(--tinta);font-family:Archivo,system-ui,sans-serif;font-size:17px;line-height:1.5;-webkit-font-smoothing:antialiased}
.hw{font-family:Kalam,'Comic Sans MS',cursive}
.slide{padding:clamp(22px,5vh,56px) 16px clamp(22px,4vh,44px);border-bottom:1.5px dashed var(--linea);display:flex;flex-direction:column}
.in{width:100%;max-width:1180px;margin:0 auto;display:flex;flex-direction:column;flex:1;min-height:0}
.n{font-family:Kalam,cursive;font-weight:700;color:var(--bronce);font-size:clamp(18px,1.6vw,22px)}
h1{font-weight:850;font-stretch:118%;font-size:clamp(30px,4.6vw,64px);line-height:1;letter-spacing:-.025em;margin:.12em 0 0;max-width:19ch;text-wrap:balance}
.cover h1{font-size:clamp(40px,6vw,86px);max-width:14ch}
.sub{font-size:clamp(17px,1.6vw,22px);color:var(--piedra);margin:.6em 0 0;max-width:46ch}
figure{margin:clamp(12px,2.4vh,28px) 0;display:flex;align-items:center;justify-content:center;flex:1;min-height:0}
figure svg{width:100%;height:auto;display:block;max-width:980px}
.bottom{display:flex;flex-direction:column;gap:12px}
.rule{font-family:Kalam,cursive;font-weight:700;font-size:clamp(23px,2.5vw,38px);line-height:1.2;margin:0;max-width:34ch}
.rule mark{background:linear-gradient(180deg,transparent 52%,var(--marca) 52%,var(--marca) 92%,transparent 92%);color:inherit;padding:0 .12em}
.hz{font-size:14.5px;color:var(--piedra);margin:0;max-width:70ch}
.notes{font-family:Kalam,cursive;font-size:clamp(17px,1.5vw,21px);line-height:1.35;margin:0;padding:0;list-style:none;display:grid;gap:4px}
.notes li{padding-left:1.1em;position:relative;max-width:62ch}
.notes li::before{content:'';position:absolute;left:0;top:.62em;width:.5em;height:2.5px;background:var(--tinta);border-radius:2px}
.checks{font-family:Kalam,cursive;font-size:clamp(17px,1.5vw,21px);margin:0}
.checks b{display:block;font-weight:700;margin-bottom:4px}
.checks ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px 22px}
.checks li::before{content:'✓ ';font-weight:700}
.brakes{font-family:Kalam,cursive;font-size:clamp(17px,1.5vw,21px);margin:0}
.brakes b{display:block;font-weight:700;margin-bottom:4px}
.brakes ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px 22px}
.brakes li::before{content:'✗ ';font-weight:700}
table{border-collapse:collapse;width:100%;font-size:clamp(14.5px,1.25vw,17px);margin:0 0 4px}
th,td{text-align:left;padding:7px 10px;border-bottom:1.5px solid var(--linea);vertical-align:top}
th{font-weight:700;font-size:13.5px;color:var(--piedra)}
td:first-child{font-weight:700}
.strip{list-style:none;margin:clamp(12px,2.4vh,28px) 0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:14px 18px;flex:1;align-content:center}
.strip li{border:2.5px solid var(--tinta);border-radius:10px;padding:10px 12px 12px;display:grid;grid-template-rows:auto auto 1fr;gap:2px}
.strip svg{width:100%;max-height:120px;height:auto}
.strip h3{font-family:Kalam,cursive;font-size:clamp(18px,1.6vw,22px);margin:4px 0 0;line-height:1.1}
.strip p{margin:0;font-size:clamp(14.5px,1.2vw,16.5px);line-height:1.35}
.hint{font-size:14px;color:var(--piedra);margin:.8em 0 0}
.book{margin:.2em 0 0;font-weight:700;font-size:16px}.book a{color:var(--tinta);text-decoration-thickness:2px;text-underline-offset:3px}.book a:focus-visible{outline:3px solid var(--bronce);outline-offset:2px}
.ctl{position:fixed;right:14px;bottom:14px;display:flex;gap:6px;align-items:center;z-index:5}
.ctl button{font:600 14px Archivo,system-ui,sans-serif;background:#fff;color:var(--tinta);border:2px solid var(--tinta);border-radius:999px;padding:6px 12px;cursor:pointer}
.ctl button:focus-visible{outline:3px solid var(--bronce);outline-offset:2px}
.ctl .cnt{font:600 14px Archivo,system-ui,sans-serif;background:#fff;border-radius:999px;padding:6px 10px}
@media (min-width:900px) and (min-height:640px){
  html{scroll-snap-type:y mandatory}
  .slide{height:100vh;height:100svh;scroll-snap-align:start;padding-left:5vw;padding-right:5vw;overflow:hidden}
  figure svg{max-height:100%}
  figure{position:relative}
  figure>svg{position:absolute;inset:0;margin:auto;width:auto;max-width:100%;height:100%}
  .tablefig figure>svg{height:100%}
  .cover h1{font-size:clamp(36px,4.6vw,68px);max-width:none}
  .cover .in{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);grid-template-rows:auto auto auto 1fr auto;column-gap:4vw}
  .cover .n,.cover h1,.cover .sub,.cover .bottom{grid-column:1}
  .cover .bottom{grid-row:5}
  .cover figure{grid-column:2;grid-row:1/6;margin:0}
}
@media (max-width:899px){.ctl{display:none}.strip{grid-template-columns:repeat(2,1fr)}}
@media (max-width:520px){.strip{grid-template-columns:1fr}.strip li{grid-template-columns:110px 1fr;grid-template-rows:auto 1fr;column-gap:12px}.strip li svg{grid-row:1/3}.hide-sm{display:none}}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
@media print{.ctl{display:none}.slide{height:auto;page-break-after:always}}
"""

JS = """
const S=[...document.querySelectorAll('.slide')];const cnt=document.querySelector('.cnt');
function cur(){let b=0,m=1e9;S.forEach((s,i)=>{const d=Math.abs(s.getBoundingClientRect().top);if(d<m){m=d;b=i}});return b}
function go(i){i=Math.max(0,Math.min(S.length-1,i));S[i].scrollIntoView({block:'start'});}
function upd(){if(cnt)cnt.textContent=(cur()+1)+' / '+S.length}
addEventListener('scroll',()=>requestAnimationFrame(upd),{passive:true});upd();
addEventListener('keydown',e=>{if(e.target.closest&&e.target.closest('input,textarea'))return;
 if(['ArrowDown','ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();go(cur()+1)}
 else if(['ArrowUp','ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(cur()-1)}
 else if(e.key==='Home'){e.preventDefault();go(0)} else if(e.key==='End'){e.preventDefault();go(S.length-1)}
 else if(e.key==='f'||e.key==='F'){fs()}});
function fs(){if(!document.fullscreenElement){document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen()}else{document.exitFullscreen()}}
document.getElementById('prev').onclick=()=>go(cur()-1);document.getElementById('next').onclick=()=>go(cur()+1);document.getElementById('full').onclick=fs;
"""

FILTER = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
          '<filter id="rough" x="-5%" y="-5%" width="110%" height="110%">'
          '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="7" result="n"/>'
          '<feDisplacementMap in="SourceGraphic" in2="n" scale="3.2" xChannelSelector="R" yChannelSelector="G"/>'
          '</filter></defs></svg>')


def slide_html(i, s):
    total = len(SLIDES)
    cls = "slide " + s.get("cls", "")
    if "table" in s:
        cls += " tablefig"
    h = [f'<section class="{cls.strip()}" id="l{i}" aria-label="Lámina {i} de {total}"><div class="in">']
    h.append(f'<div class="n">{i} / {total}</div>')
    h.append(f'<h1>{esc(s["title"])}</h1>')
    if s.get("sub"):
        h.append(f'<p class="sub">{esc(s["sub"])}</p>')
    if s.get("strip"):
        h.append('<ol class="strip">')
        for k, ttl, txt in STRIP:
            h.append(f'<li>{mini(k)}<h3>{k}. {esc(ttl)}</h3><p>{esc(txt)}</p></li>')
        h.append('</ol>')
    else:
        h.append(f'<figure>{s["fig"]}</figure>')
    h.append('<div class="bottom">')
    if s.get("table"):
        h.append('<table><thead><tr><th>Rubro</th><th>Puerta (front end)</th><th>Sala (back end)</th></tr></thead><tbody>')
        for a, b, c in s["table"]:
            h.append(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>')
        h.append('</tbody></table>')
    if s.get("checks"):
        h.append(f'<div class="checks"><b>{esc(s["checks_title"])}</b><ul>' + "".join(f'<li>{esc(c)}</li>' for c in s["checks"]) + '</ul></div>')
    if s.get("note"):
        h.append(f'<ul class="notes"><li>{esc(s["note"])}</li></ul>')
    if s.get("notes"):
        h.append('<ul class="notes">' + "".join(f'<li>{esc(n)}</li>' for n in s["notes"]) + '</ul>')
    if s.get("brakes"):
        h.append('<div class="brakes"><b>Los 5 frenos que nunca dejamos pasar:</b><ul>' + "".join(f'<li>{esc(c)}</li>' for c in s["brakes"]) + '</ul></div>')
    h.append(f'<p class="rule"><mark>{esc(s["rule"])}</mark></p>')
    if s.get("hz"):
        h.append(f'<p class="hz">{esc(s["hz"])}</p>')
    if i == 1:
        h.append('<p class="book"><a href="La-maquina-de-clientas-de-alto-valor.pdf" download>Descargar el libro en PDF</a></p>')
        h.append('<p class="hint hide-sm">Para presentar: flechas del teclado para avanzar y la tecla F para pantalla completa.</p>')
    h.append('</div></div></section>')
    return "".join(h)


def build():
    body = "".join(slide_html(i + 1, s) for i, s in enumerate(SLIDES))
    html = ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow">'
            '<title>La máquina de alto valor</title>'
            f'<style>{CSS}</style></head><body>{FILTER}<main>{body}</main>'
            '<nav class="ctl" aria-label="Navegación de láminas"><button id="prev" aria-label="Lámina anterior">Anterior</button>'
            '<span class="cnt" aria-live="polite"></span><button id="next" aria-label="Lámina siguiente">Siguiente</button>'
            '<button id="full">Pantalla completa</button></nav>'
            f'<script>{JS}</script></body></html>')
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("ok", len(html))


if __name__ == "__main__":
    build()
