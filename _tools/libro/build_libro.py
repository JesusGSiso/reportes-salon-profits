"""Construye el libro 'La máquina de clientas de alto valor' en PDF (6 x 9 pulgadas)."""
import asyncio, importlib.util, os, re, sys
from html import escape as esc
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bm", os.path.join(HERE, "..", "maquina.py"))
bm = importlib.util.module_from_spec(spec); spec.loader.exec_module(bm)
t, tl, rect, arrow, svg, line = bm.t, bm.tl, bm.rect, bm.arrow, bm.svg, bm.line
INK, STONE, BRONZE, MARK = bm.INK, bm.STONE, bm.BRONZE, bm.MARK

HTML_OUT = os.path.join(HERE, "libro.html")
PDF_OUT = os.path.join(HERE, "La-maquina-de-clientas-de-alto-valor.pdf")


def d_ecuacion():
    S, T = [], []
    T.append(t(30, 186, "valor =", 46, "start", 700))
    boxes = [(230, 60, 290, "resultado soñado", "up", "una cara sin manchas"),
             (560, 60, 320, "seguridad de lograrlo", "up", "antes y después, escáner"),
             (230, 210, 290, "tiempo", "down", "cambio desde la 1.ª sesión"),
             (560, 210, 320, "esfuerzo", "down", "rutina y crema en casa")]
    for x, y, w, lab, d, ex in boxes:
        S.append(rect(x, y, w, 66, 10, 4, "#fff"))
        T.append(t(x + (w - 34) / 2, y + 43, lab, 28, "middle", 700))
        ax = x + w - 26
        if d == "up":
            S.append(arrow(ax, y + 52, ax, y + 16, 0, 4, 11, BRONZE))
        else:
            S.append(arrow(ax, y + 16, ax, y + 52, 0, 4, 11, BRONZE))
        ey = y + 98 if y > 100 else y - 18
        T.append(t(x + w / 2, ey, ex, 22, "middle", 400, STONE))
    T.append(t(540, 103, "×", 34, "middle", 700)); T.append(t(540, 253, "×", 34, "middle", 700))
    S.append(line(220, 168, 885, 168, 5))
    T.append(t(30, 225, "arriba: sube", 22, "start", 400, STONE)); T.append(t(30, 250, "abajo: baja", 22, "start", 400, STONE))
    return svg((900, 330), "".join(S), "".join(T))


FIGS = {
    "mismo_dinero": bm.d_mismo_dinero, "dolor": bm.d_dolor, "buffet": bm.d_buffet,
    "dos_ofertas": bm.d_dos_ofertas, "anuncio": bm.d_anuncio, "oferta": bm.d_oferta,
    "ecuacion": d_ecuacion, "precio": bm.d_precio, "vitrina": bm.d_vitrina,
    "consulta": bm.d_consulta, "escalera": bm.d_escalera, "maquina": bm.d_maquina,
    "tablero": bm.d_tablero, "portada": bm.d_portada,
}

GLOSSARY = [
    ("Servicio ancla", "El servicio de alto valor con el que la dueña sale al mercado. Va en los anuncios, en la vitrina y en la consulta."),
    ("Puerta (front end)", "La oferta de atracción: lo que mostramos en el anuncio para que llegue la persona con el problema. Por ejemplo, un escáner facial gratis. Hormozi la llama lead magnet u oferta de atracción."),
    ("Sala (back end)", "La oferta irresistible que la dueña vende cuando la persona ya está adentro. Por ejemplo, un programa de manchas de $1,500. Hormozi la llama Grand Slam Offer u oferta principal."),
    ("Transformación", "Como le decimos a la oferta de la sala. No le decimos paquete."),
    ("Vitrina", "El perfil de Instagram de la dueña: las 16 publicaciones del servicio ancla, con su cara, y una bio que lleva a agendar."),
    ("Lead", "Una persona que mostró interés: escribió, preguntó o dejó sus datos. Todavía no es clienta."),
    ("Tasa de agendamiento", "De las que escriben, cuántas agendan una cita."),
    ("Asistencia (show rate)", "De las que agendan, cuántas llegan a la cita."),
    ("Tasa de cierre", "De las que llegan, cuántas compran."),
    ("Costo por clienta", "Lo que se invierte en anuncios dividido entre las clientas nuevas que compraron."),
    ("Upsell", "Lo siguiente que se le ofrece a una clienta que ya compró, porque le sirve justo después."),
    ("Downsell", "Lo que se ofrece cuando dice que no: otra forma de pago o menos alcance. Nunca lo mismo más barato."),
    ("Continuidad", "Un servicio que se paga cada mes porque da valor cada mes, como un mantenimiento o una suscripción."),
    ("Commodity", "Lo que el mercado ve igual en todas partes y por eso solo compara por precio."),
]

WORKSHEET = [
    ("Rubro y zona", 1), ("Factura hoy y quiere facturar", 1), ("El dolor, con palabras de su clienta", 2),
    ("Servicio ancla (¿pasa las 5 preguntas?)", 1), ("La puerta: oferta de atracción", 1),
    ("El anuncio: cómo llama, qué promete, a qué invita", 2), ("La sala: nombre, componentes y precio", 2),
    ("Si dice «está caro»: plan de pagos y versión corta", 1), ("Adentro: siguiente compra y algo mensual", 1),
    ("Clientas al mes que necesita para su meta", 1),
]

PARTS = {}

CSS = r"""
@font-face{font-family:Archivo;src:url(fonts/archivo.woff2) format('woff2');font-weight:100 900;font-stretch:62% 125%}
@font-face{font-family:Kalam;src:url(fonts/kalam-400.woff2) format('woff2');font-weight:400}
@font-face{font-family:Kalam;src:url(fonts/kalam-700.woff2) format('woff2');font-weight:700}
@page{size:6in 9in;margin:0.72in 0.68in 0.78in 0.68in;
  @bottom-center{content:counter(page);font:500 8.5pt Archivo,sans-serif;color:#5C5249}}
@page cover{margin:0;@bottom-center{content:none}}
@page plain{@bottom-center{content:none}}
:root{--tinta:#1A1612;--piedra:#5C5249;--bronce:#7A5C2E;--marca:#EBDDBF;--linea:#E4D9CA;--crema:#F6F0EA}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font-family:Archivo,sans-serif;font-size:10pt;line-height:1.56;color:var(--tinta);orphans:3;widows:3}
.hw{font-family:Kalam,cursive}
p{margin:0 0 .72em}
strong{font-weight:750}
em{font-style:italic}
h1,h2,h3{break-after:avoid}
h3{font-weight:800;font-stretch:110%;font-size:12pt;line-height:1.2;margin:1.35em 0 .45em;letter-spacing:-.005em}
ul,ol{margin:0 0 .8em;padding-left:1.35em}
li{margin:0 0 .35em;padding-left:.15em}
ol li::marker{font-weight:800}
table{width:100%;border-collapse:collapse;font-size:8.6pt;line-height:1.38;margin:.5em 0 1.1em;break-inside:avoid}
th{text-align:left;font-weight:750;border-bottom:1.6px solid var(--tinta);padding:4px 6px 4px 0;vertical-align:bottom}
td{border-bottom:1px solid var(--linea);padding:5px 6px 5px 0;vertical-align:top}
td:first-child{font-weight:700}
figure{margin:.4em 0 1.1em;break-inside:avoid;text-align:center}
figure svg{width:100%;height:auto;max-height:3.5in}

/* capítulos */
.chapter{break-before:page}
.ch-head{margin:0 0 .5em}
.ch-part{font-size:8.5pt;color:var(--piedra);font-weight:500;margin-bottom:.2em}
.ch-num{font-family:Kalam,cursive;font-weight:700;color:var(--bronce);font-size:15pt;line-height:1.1}
.chapter h1{font-weight:850;font-stretch:118%;font-size:24pt;line-height:1.03;letter-spacing:-.025em;margin:.1em 0 .25em}

/* regla */
.rule{break-inside:avoid;margin:1.4em 0 .4em;padding:.9em 0 .2em;border-top:2px solid var(--tinta)}
.rule .lab{display:block;font-size:8pt;color:var(--piedra);font-weight:600;margin-bottom:.15em}
.rule .txt{font-family:Kalam,cursive;font-weight:700;font-size:16.5pt;line-height:1.22}
.rule mark{background:linear-gradient(180deg,transparent 52%,var(--marca) 52%,var(--marca) 92%,transparent 92%);color:inherit;padding:0 .08em;-webkit-box-decoration-break:clone;box-decoration-break:clone}

/* recuadros */
.box{break-inside:avoid;border-radius:8px;padding:.75em .9em .35em;margin:1.1em 0;font-size:9.3pt;line-height:1.5}
.box-t{font-family:Kalam,cursive;font-weight:700;font-size:12pt;line-height:1.1;margin-bottom:.35em}
.box p{margin:0 0 .5em}
.hz{background:var(--crema);border:1.5px solid var(--tinta)}
.hz .box-t::before{content:'';display:inline-block;width:.55em;height:.55em;background:var(--bronce);border-radius:50%;margin-right:.4em;vertical-align:.08em}
.ej{border:1.6px dashed var(--piedra)}
.acc{border:2px solid var(--tinta)}
.acc ul{list-style:none;padding-left:0;margin:0 0 .4em}
.acc li{position:relative;padding-left:1.45em}
.acc li::before{content:'';position:absolute;left:0;top:.22em;width:.82em;height:.82em;border:1.6px solid var(--tinta);border-radius:2px}

/* portada */
.cover{page:cover;width:6in;height:9in;position:relative;overflow:hidden;display:flex;flex-direction:column;padding:.62in .6in 0}
.cover .brand{font-family:Kalam,cursive;font-weight:700;color:var(--bronce);font-size:14pt}
.cover h1{font-weight:850;font-stretch:120%;font-size:37pt;line-height:1;letter-spacing:-.03em;margin:.25em 0 .3em;text-wrap:balance}
.cover .sub{font-size:12pt;line-height:1.35;color:var(--piedra);margin:0;max-width:4.2in}
.cover figure{margin:.35in 0 0;flex:1}
.cover figure svg{max-height:2.7in}
.cover .band{position:absolute;left:0;right:0;bottom:0;height:1.25in;background:var(--tinta);color:#fff;padding:.32in .6in;display:flex;flex-direction:column;justify-content:center}
.cover .band .au{font-weight:800;font-stretch:112%;font-size:15pt;letter-spacing:-.01em}
.cover .band .ed{font-size:8.5pt;color:#D9CFC2;margin-top:.2em}

/* créditos e índice */
.credits{page:plain;break-before:page;height:7.4in;display:flex;flex-direction:column;justify-content:flex-end;font-size:8.3pt;line-height:1.5;color:var(--piedra)}
.credits p{margin:0 0 .7em}
.credits b{color:var(--tinta)}
.toc{page:plain;break-before:page}
.toc h1{font-weight:850;font-stretch:118%;font-size:24pt;line-height:1.2;padding-top:4pt;margin:0 0 .5em;letter-spacing:-.02em}
.keep{break-inside:avoid}
.toc .part{font-size:8.5pt;color:var(--piedra);font-weight:600;margin:1em 0 .2em}
.toc a{display:flex;align-items:baseline;gap:6px;color:inherit;text-decoration:none;font-size:10pt;line-height:1.3;padding:.24em 0;border-bottom:1px solid var(--linea)}
.toc a .n{font-family:Kalam,cursive;font-weight:700;color:var(--bronce);width:1.6em;flex:none}
.toc a .ti{flex:1}
.toc a .pg{font-weight:700;font-variant-numeric:tabular-nums}

/* tira y hoja */
.strip{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:.3em 0 1.1em;break-inside:avoid}
.strip div{border:1.6px solid var(--tinta);border-radius:7px;padding:4px 6px 6px;font-size:7.6pt;line-height:1.3}
.strip svg{width:100%;height:auto;max-height:.85in}
.strip b{display:block;font-family:Kalam,cursive;font-size:10pt;margin:2px 0 1px}
.ws{break-before:page}
.ws .row{break-inside:avoid;margin:0 0 .35em}
.ws .lab{font-weight:700;font-size:9.4pt}
.ws .ln{height:.27in;border-bottom:1.3px solid var(--piedra)}
.rules-list{list-style:none;padding:0;margin:.4em 0 0;counter-reset:r}
.rules-list li{counter-increment:r;display:flex;gap:.6em;align-items:baseline;padding:.26em 0;border-bottom:1px solid var(--linea);break-inside:avoid}
.rules-list li::before{content:counter(r);font-family:Kalam,cursive;font-weight:700;color:var(--bronce);font-size:12pt;width:1.3em;flex:none}
.rules-list .txt{font-family:Kalam,cursive;font-weight:700;font-size:11.6pt;line-height:1.2}
.rules-list .src{font-size:7.8pt;color:var(--piedra);margin-left:auto;white-space:nowrap;padding-left:.6em}
dl.gl{margin:.4em 0 0}
dl.gl dt{font-weight:750;font-size:9.6pt;margin-top:.55em;break-after:avoid}
dl.gl dd{margin:.1em 0 0;font-size:9.2pt;line-height:1.45}
.sources{margin-top:1.4em;font-size:8.4pt;color:var(--piedra);line-height:1.45;break-inside:avoid}
.back{page:plain;break-before:page;height:7.4in;display:flex;flex-direction:column;justify-content:center;text-align:left}
.back .txt{font-family:Kalam,cursive;font-weight:700;font-size:24pt;line-height:1.15}
.back mark{background:linear-gradient(180deg,transparent 52%,var(--marca) 52%,var(--marca) 92%,transparent 92%);color:inherit}
.back figure svg{max-height:2.2in}
.back .ed{font-size:8.5pt;color:var(--piedra);margin-top:1.2em}
"""


def md(text):
    return markdown.markdown(text, extensions=["tables"], output_format="html")


def parse(src):
    lines = src.split("\n")
    out, buf, rules, toc = [], [], [], []
    cur = {"open": False}
    i = 0

    def flush():
        if buf:
            txt = "\n".join(buf)
            if txt.strip():
                out.append(md(txt))
            buf.clear()

    def close_section():
        flush()
        if cur["open"]:
            out.append("</section>")
            cur["open"] = False

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("@front "):
            close_section()
            label, title = [x.strip() for x in ln[7:].split("|")]
            out.append(f'<section class="chapter" id="front"><div class="ch-head"><div class="ch-num">{esc(label)}</div><h1>{esc(title)}</h1></div>')
            cur["open"] = True; cur["ch"] = label
            toc.append(("front", None, label, None))
        elif ln.startswith("@chapter "):
            close_section()
            num, part, title = [x.strip() for x in ln[9:].split("|")]
            out.append(f'<section class="chapter" id="cap-{num}"><div class="ch-head"><div class="ch-part">{esc(part)}</div>'
                       f'<div class="ch-num">Capítulo {num}</div><h1>{esc(title)}</h1></div>')
            cur["open"] = True; cur["ch"] = f"Capítulo {num}"
            toc.append((f"cap-{num}", num, title, part))
        elif ln.startswith("@fig "):
            flush(); out.append(f'<figure>{FIGS[ln[5:].strip()]()}</figure>')
        elif ln.startswith("@rule "):
            flush(); txt = ln[6:].strip(); rules.append((txt, cur.get("ch", "")))
            rule = f'<div class="rule"><span class="lab">La regla</span><span class="txt"><mark>{esc(txt)}</mark></span></div>'
            if out and out[-1].startswith('<aside class="box acc"'):
                out.append(f'<div class="keep">{out.pop()}{rule}</div>')
            else:
                out.append(rule)
        elif ln.strip() == "@strip":
            flush()
            cells = "".join(f'<div>{bm.mini(k)}<b>{k}. {esc(a)}</b>{esc(b)}</div>' for k, a, b in bm.STRIP)
            out.append(f'<div class="strip">{cells}</div>')
        elif ln.strip() in ("@worksheet", "@rules", "@glossary"):
            close_section()
            out.append(f"<!--{ln.strip()}-->")
        elif ln.startswith(":::"):
            flush()
            head = ln[3:].strip()
            kind, _, title = head.partition(" ")
            body = []
            i += 1
            while not lines[i].startswith(":::"):
                body.append(lines[i]); i += 1
            inner = md("\n".join(body))
            if kind == "hormozi":
                out.append(f'<aside class="box hz"><div class="box-t">Lo que dice Hormozi</div>{inner}</aside>')
            elif kind == "account":
                out.append(f'<aside class="box acc"><div class="box-t">Lo que haces tú</div>{inner}</aside>')
            elif kind == "ejemplo":
                out.append(f'<aside class="box ej"><div class="box-t">Ejemplo: {esc(title)}</div>{inner}</aside>')
        else:
            buf.append(ln)
        i += 1
    close_section()
    return "".join(out), rules, toc


def cover():
    return ('<section class="cover"><div class="brand">Salon Profits</div>'
            '<h1>La máquina de clientas de alto valor</h1>'
            '<p class="sub">Manual para las accounts: cómo le damos el éxito a cada clienta</p>'
            f'<figure>{bm.d_portada()}</figure>'
            '<div class="band"><div class="au">Jesús Gabriel Gómez</div><div class="ed">Salon Profits by Vivas Mastery LLC</div></div></section>')


def credits():
    return ('<section class="credits">'
            '<p><b>La máquina de clientas de alto valor</b><br>Manual para las accounts de Salon Profits</p>'
            '<p>Primera edición, noviembre de 2026. Uso interno del equipo de Salon Profits by Vivas Mastery LLC.</p>'
            '<p>Este manual nace de las llamadas de cierre de Salon Profits entre el 19 de octubre y el 6 de noviembre de 2026, '
            'y aplica los marcos de los libros <i>$100M Offers</i>, <i>$100M Leads</i> y <i>$100M Money Models</i> de Alex Hormozi. '
            'Los marcos están explicados con nuestras palabras; para el detalle, ve a los libros.</p>'
            '<p>Los ejemplos usan el rubro de cada clienta en lugar de su nombre. Los casos marcados "para afinar" son ilustrativos.</p>'
            '</section>')


def toc_html(toc, pages):
    rows = ['<section class="toc"><h1>Índice</h1>']
    last_part = None
    def row(anchor, n, title):
        pg = pages.get(anchor, "00")
        return (f'<a href="#{anchor}"><span class="n">{n or ""}</span><span class="ti">{esc(title)}</span>'
                f'<span class="pg">{pg}</span></a>')
    for anchor, n, title, part in toc:
        if part and part != last_part:
            rows.append(f'<div class="part">{esc(part)}</div>'); last_part = part
        rows.append(row(anchor, n, title))
    rows.append('<div class="part">Para usar</div>')
    rows.append(row("hoja", None, "La hoja de la máquina"))
    rows.append(row("reglas", None, "Las reglas de la máquina"))
    rows.append(row("glosario", None, "Glosario"))
    rows.append('</section>')
    return "".join(rows)


def worksheet():
    rows = "".join(f'<div class="row"><div class="lab">{esc(l)}</div>' + '<div class="ln"></div>' * n + '</div>' for l, n in WORKSHEET)
    return ('<section class="chapter ws" id="hoja"><div class="ch-head"><div class="ch-num">Para usar</div><h1>La hoja de la máquina</h1></div>'
            '<p>Llénala con cada clienta en la reunión estratégica. Si una línea queda vacía, ahí hay trabajo por hacer.</p>'
            f'{rows}</section>')


def rules_page(rules):
    items = "".join(f'<li><span class="txt">{esc(r)}</span><span class="src">{esc(c)}</span></li>' for r, c in rules)
    return ('<section class="chapter" id="reglas"><div class="ch-head"><div class="ch-num">Para usar</div><h1>Las reglas de la máquina</h1></div>'
            '<p>Todo el manual, en una página. Si tienes una duda con una clienta, empieza por aquí.</p>'
            f'<ol class="rules-list">{items}</ol></section>')


def glossary():
    items = "".join(f'<dt>{esc(a)}</dt><dd>{esc(b)}</dd>' for a, b in GLOSSARY)
    return ('<section class="chapter" id="glosario"><div class="ch-head"><div class="ch-num">Para usar</div><h1>Glosario</h1></div>'
            f'<dl class="gl">{items}</dl>'
            '<div class="sources"><b>Fuentes.</b> Llamadas de cierre de Salon Profits, del 19 de octubre al 6 de noviembre de 2026. '
            'Alex Hormozi, <i>$100M Offers</i> (2021), <i>$100M Leads</i> (2023) y <i>$100M Money Models</i> (2025).</div></section>')


def back():
    return ('<section class="back"><div class="txt"><mark>No le traemos clientas.</mark><br><mark>Le traemos dinero.</mark></div>'
            f'<figure>{bm.d_portada()}</figure><div class="ed">Salon Profits by Vivas Mastery LLC</div></section>')


def build_html(pages):
    src = open(os.path.join(HERE, "libro.md"), encoding="utf-8").read()
    body, rules, toc = parse(src)
    body = body.replace("<!--@worksheet-->", worksheet()).replace("<!--@rules-->", rules_page(rules)).replace("<!--@glossary-->", glossary())
    html = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><title>La máquina de clientas de alto valor</title>'
            f'<style>{CSS}</style></head><body>{bm.FILTER}'
            f'{cover()}{credits()}{toc_html(toc, pages)}{body}{back()}</body></html>')
    open(HTML_OUT, "w", encoding="utf-8").write(html)
    return toc


async def render(path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page()
        await pg.goto("file://" + HTML_OUT); await pg.wait_for_timeout(700)
        await pg.evaluate("document.fonts.ready")
        await pg.pdf(path=path, prefer_css_page_size=True, print_background=True, outline=True, tagged=True)
        await b.close()


def find_pages(pdf, toc):
    import pdfplumber
    texts = []
    with pdfplumber.open(pdf) as d:
        for p in d.pages:
            texts.append(re.sub(r"\s+", " ", p.extract_text() or ""))
    start = next(i for i, tx in enumerate(texts) if "Tu trabajo no es publicar" in tx and "Índice" not in tx)
    pages = {}
    def first(pattern):
        for i in range(start, len(texts)):
            if re.search(pattern, texts[i]):
                return i + 1
    pages["front"] = first(r"Antes de empezar")
    for anchor, n, title, part in toc:
        if n:
            pages[anchor] = first(rf"Capítulo {n}(?!\d)")
    pages["hoja"] = first(r"La hoja de la máquina")
    pages["reglas"] = first(r"Las reglas de la máquina")
    pages["glosario"] = first(r"Glosario")
    return pages, len(texts)


def main():
    toc = build_html({})
    tmp = os.path.join(HERE, "pass1.pdf")
    asyncio.run(render(tmp))
    pages, n = find_pages(tmp, toc)
    print("pass1 pages:", n, pages)
    build_html(pages)
    asyncio.run(render(tmp))
    pages2, n2 = find_pages(tmp, toc)
    assert pages2 == pages, (pages, pages2)
    from pypdf import PdfWriter
    w = PdfWriter(clone_from=tmp)
    w.add_metadata({"/Title": "La máquina de clientas de alto valor", "/Author": "Jesús Gabriel Gómez",
                    "/Subject": "Manual para las accounts de Salon Profits", "/Creator": "Salon Profits"})
    with open(PDF_OUT, "wb") as f:
        w.write(f)
    os.remove(tmp)
    print("ok", n2, "páginas", os.path.getsize(PDF_OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
