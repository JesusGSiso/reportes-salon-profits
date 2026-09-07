#!/usr/bin/env python3
"""
Escribe el sitio en el repo a partir de los datos de /tmp/gestion.

Lee todos los /tmp/gestion/<slug>/pagina.json y /tmp/gestion/triage.json y
escribe, dentro del repo:
  index.html                  (raiz neutra, no lista a nadie)
  <slug>/index.html           (seccion 5: el JSON dentro de la plantilla)
  equipo/triage/index.html    (seccion 8: HTML completo y autonomo)

Uso: build.py <repo> [carpeta_datos]   (carpeta_datos por defecto /tmp/gestion)

No borra nada: sobreescribe solo lo suyo. Imprime solo lo que escribio.
"""
import glob
import html
import json
import os
import sys

REPO = sys.argv[1]
DATOS = sys.argv[2] if len(sys.argv) > 2 else "/tmp/gestion"

RAIZ = ('<!doctype html><html lang="es"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Reportes · Salon Profits</title><style>'
        'body{font:16px system-ui,sans-serif;background:#F7F6F2;color:#1F2421;'
        'display:flex;min-height:100vh;align-items:center;justify-content:center;'
        'margin:0;padding:24px;text-align:center}div{max-width:420px}'
        'h1{font-family:Georgia,serif;font-size:26px;font-weight:600;margin:0 0 10px}'
        'p{color:#6B6B63;font-size:15px;line-height:1.5;margin:0}</style>'
        '<div><h1>Reportes de gestión</h1><p>Cada reporte tiene su propio '
        'enlace privado. Si no tienes el tuyo, pídeselo a tu equipo de '
        'Salon Profits.</p></div></html>')

PAGINA = ('<!doctype html><html lang="es"><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          '<title>Reporte de Gestión</title>'
          '<link rel="stylesheet" href="/assets/s.css">'
          '<script type="application/json" id="d">%s</script>'
          '<script src="/assets/a.js" defer></script></html>')

TRIAGE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#F7F6F2;color:#1F2421;font:15px/1.5 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;padding:0 0 56px}
.w{max-width:1080px;margin:0 auto;padding:0 18px}
header{background:#24534E;color:#fff;padding:26px 0 22px;margin-bottom:22px}
h1{font-family:Georgia,serif;font-size:26px;font-weight:600}
.eb{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:#BFD6D1;margin-bottom:6px}
h2{font-family:Georgia,serif;font-size:19px;color:#24534E;margin:30px 0 10px;font-weight:600}
.cart{background:#fff;border:1px solid #E6E2D9;border-radius:12px;padding:18px 20px}
.cart .big{font-family:Georgia,serif;font-size:30px;font-weight:700;color:#2F6F68;line-height:1.2}
.cart .d{font-size:14px;color:#1F2421;margin-top:4px}
.cart .a{font-size:13px;color:#6B6B63;margin-top:2px}
table{width:100%;table-layout:fixed;border-collapse:collapse;background:#fff;border:1px solid #E6E2D9;border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:10px 9px;font-size:13px;vertical-align:top;border-bottom:1px solid #EFEDE7;word-wrap:break-word;overflow-wrap:anywhere}
th{background:#EFEDE7;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:#4A4A44;font-weight:700}
tr:last-child td{border-bottom:none}
td a{color:#24534E;font-weight:600}
.tasa{font-family:Georgia,serif;font-size:19px;font-weight:700;color:#C0522F}
.tasa.ok{color:#3F7D4A}.tasa.md{color:#B0741C}
.nil{font-size:12.5px;color:#6B6B63;font-style:italic}
.ant{font-size:11.5px;color:#6B6B63;display:block}
.sig{background:#FBEDE7;border:1px solid #EBD5CB;border-radius:12px;padding:16px 18px;margin-bottom:10px}
.sig b{color:#8F3D1F}
.ok2{background:#E8F0EE;border:1px solid #CFE0DC;border-radius:12px;padding:16px 18px;font-size:14px;color:#24534E}
ul{margin:6px 0 0 18px}li{font-size:14px;margin-bottom:4px}
pre{background:#1F2421;color:#D9E4E1;border-radius:12px;padding:16px;font-size:11.5px;line-height:1.6;white-space:pre-wrap;word-break:break-word;overflow-wrap:anywhere;margin-top:8px}
.note{font-size:13px;color:#6B6B63;margin-top:8px}
@media(max-width:900px){
 table,thead,tbody,th,td,tr{display:block}
 thead{display:none}
 table{border:none;background:none}
 tr{background:#fff;border:1px solid #E6E2D9;border-radius:12px;margin-bottom:10px;padding:6px 4px}
 td{border-bottom:none;padding:5px 12px;display:flex;justify-content:space-between;gap:14px}
 td:before{content:attr(data-l);font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:#6B6B63;font-weight:700;flex:none}
 td>span,td>a{text-align:right}
}
"""

COLS = [("Clienta", "cli"), ("Leads", "leads"), ("Agendaron", "agend"),
        ("Tasa", "tasa"), ("Quién agendó", "quien"),
        ("Antes de agendar", "antes"), ("Después de agendar", "despues")]


def e(x):
    return html.escape(str(x if x is not None else ""), quote=True)


def escribir(ruta, contenido):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w") as f:
        f.write(contenido)
    print("escrito:", os.path.relpath(ruta, REPO))


def triage(t):
    c = t["cartera"]
    h = ['<!doctype html><html lang="es"><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>Triage · %s</title>' % e(t.get("rangoCorto", "")),
         '<style>%s</style>' % TRIAGE_CSS,
         '<header><div class="w"><div class="eb">Salon Profits · uso interno</div>',
         '<h1>Triage de gestión — semana del %s</h1></div></header>' % e(t.get("rangoCorto", "")),
         '<div class="w">',
         '<h2>La cartera esta semana</h2><div class="cart">',
         '<div class="big">%s leads · %s agendaron · %s de agendamiento</div>'
         % (e(c["leads"]), e(c["agendaron"]),
            ("%s%%" % c["tasa"]) if c.get("tasa") is not None else "sin tasa"),
         '<div class="d">%s</div>' % e(c.get("desglose", "")),
         '<div class="a">%s</div>' % e(c.get("nota", "")),
         '</div>']

    h.append('<h2>Clienta por clienta</h2><table><thead><tr>')
    h += ['<th>%s</th>' % e(n) for n, _ in COLS]
    h.append('</tr></thead><tbody>')
    for f in t["filas"]:
        pct = f.get("tasa")
        if pct is None:
            celda = '<span class="nil">no le entraron leads</span>'
        else:
            cls = "ok" if pct >= 25 else ("md" if pct >= 12 else "")
            ant = ("" if f.get("tasaAnt") is None
                   else '<span class="ant">antes: %s%%</span>' % f["tasaAnt"])
            celda = '<span class="tasa %s">%s%%</span>%s' % (cls, pct, ant)
        url = f.get("url", "")
        cli = ('<a href="%s">%s</a>' % (e(url), e(f["nombre"])) if url
               else '<span>%s</span>' % e(f["nombre"]))
        vals = {
            "cli": cli,
            "leads": '<span>%s<span class="ant">antes: %s</span></span>'
                     % (e(f.get("leads")), e(f.get("leadsAnt"))),
            "agend": '<span>%s</span>' % e(f.get("agendaron")),
            "tasa": celda,
            "quien": '<span>%s</span>' % e(f.get("quien", "")),
            "antes": '<span>%s</span>' % e(f.get("antes", "")),
            "despues": '<span>%s</span>' % e(f.get("despues", "")),
        }
        h.append('<tr>' + "".join(
            '<td data-l="%s">%s</td>' % (e(n), vals[k]) for n, k in COLS) + '</tr>')
    h.append('</tbody></table>')
    if t.get("notaTabla"):
        h.append('<p class="note">%s</p>' % e(t["notaTabla"]))

    h.append('<h2>Señal de sistema — problema nuestro</h2>')
    if t.get("senales"):
        for s in t["senales"]:
            h.append('<div class="sig"><b>%s</b><br>%s</div>'
                     % (e(s.get("t", "")), e(s.get("d", ""))))
    else:
        h.append('<div class="ok2">Ninguna señal de sistema esta semana: '
                 'ninguna cuenta se quedó sin bot con leads entrando.</div>')

    h.append('<h2>Sin medir</h2>')
    if t.get("saltadas"):
        h.append('<ul>' + "".join('<li>%s</li>' % e(s) for s in t["saltadas"]) + '</ul>')
    else:
        h.append('<p class="note">Ninguna: todas las clientas con '
                 '<code>informe-gestion</code> se midieron esta semana.</p>')

    h.append('<h2>Apéndice</h2><pre>%s</pre>' % e(t.get("apendice", "")))
    h.append('</div></html>')
    return "".join(h)


def main():
    for ruta in sorted(glob.glob(os.path.join(DATOS, "*", "pagina.json"))):
        d = json.load(open(ruta))
        escribir(os.path.join(REPO, d["slug"], "index.html"),
                 PAGINA % json.dumps(d, ensure_ascii=False))

    escribir(os.path.join(REPO, "index.html"), RAIZ)

    ruta_t = os.path.join(DATOS, "triage.json")
    if os.path.exists(ruta_t):
        escribir(os.path.join(REPO, "equipo", "triage", "index.html"),
                 triage(json.load(open(ruta_t))))


if __name__ == "__main__":
    main()
