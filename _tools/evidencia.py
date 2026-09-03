#!/usr/bin/env python3
"""
Evidencia para redactar la pagina: la UNICA exploracion de mensajes permitida.

Uso: evidencia.py <carpeta_slug> <D>
  Lee contactos.json, mensajes.json y citas.json de esa carpeta (los compactos
  de la seccion 3) y usa las mismas definiciones de gestion_semanal.py, asi que
  nunca contradice a resumen.json. Imprime menos de 40 lineas.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gestion_semanal as G

d, fin = sys.argv[1], sys.argv[2]
C = json.load(open(f"{d}/contactos.json"))
M, _ = G.deduplicar(json.load(open(f"{d}/mensajes.json")))
A = json.load(open(f"{d}/citas.json"))
ini, finu = G.semana(fin, 0)


def en_semana(c):
    t = G.ts(c.get("dateAdded"))
    return t is not None and ini <= t <= finu


def nom(c):
    p = (c.get("firstName") or c.get("contactName") or "").strip().split()
    return p[0].title() if p else "Sin nombre"


def txt(m):
    b = re.sub(r"🔁?\s*Sent from another device.*", "", m.get("body") or "", flags=re.I | re.S).strip()
    if not b:
        b = "[audio]" if G.es_audio(m) else "[imagen]" if G.es_imagen(m) else "[adjunto]"
    return b[:90].replace("\n", " ")


def f(t):
    return t.astimezone(G.HUSO).strftime("%d/%m %H:%M")


leads = {c["id"]: c for c in C if G.es_lead_de_anuncio(c) and en_semana(c)}
por = {}
for m in M:
    cid, t = m.get("contactId"), G.ts(m.get("dateAdded"))
    if cid in leads and t and t <= finu:
        por.setdefault(cid, []).append((t, m))
con_cita = {a.get("contactId") for a in A if a.get("contactId") in leads and not a.get("deleted")}

PRECIO = re.compile(r"precio|cu[aá]nto (cuesta|vale|sale)|costo|valor", re.I)
GEN = re.compile(r"sigues interesad|sigo a la orden|a[uú]n te interesa|quedo atenta|cualquier duda", re.I)
sin, precio, gen, dias = [], [], [], {}
for cid, c in leads.items():
    ms = sorted(por.get(cid, []), key=lambda x: x[0])
    ella = [(t, m) for t, m in ms if m.get("direction") == "outbound" and G.es_de_ella(m)]
    inb = [(t, m) for t, m in ms if m.get("direction") == "inbound"]
    for t, m in ella:
        dias[f(t)[:5]] = dias.get(f(t)[:5], 0) + 1
    if not ella:
        ult = f(inb[-1][0]) + " " + txt(inb[-1][1]) if inb else "(no escribio)"
        sin.append((nom(c), "cita SI" if cid in con_cita else "cita no", f"{len(inb)} msgs", ult))
    for t, m in inb:
        if PRECIO.search(m.get("body") or ""):
            r = next(((t2, m2) for t2, m2 in ms if t2 > t and m2.get("direction") == "outbound"), None)
            quien = "ella" if r and G.es_de_ella(r[1]) else "bot" if r else "nadie"
            precio.append((nom(c), f(t), txt(m), quien, txt(r[1]) if r else ""))
            break
    for t, m in ella:
        if GEN.search(m.get("body") or ""):
            gen.append((nom(c), f(t), txt(m)))
            break

print(f"LEADS {len(leads)} | sin mensaje de ella {len(sin)} | preguntaron precio {len(precio)} | seguimiento generico {len(gen)}")
print("MENSAJES DE ELLA A LEADS POR DIA:", dict(sorted(dias.items())))
print("\n== SIN NINGUN MENSAJE DE ELLA (nombre | cita | msgs de la lead | ultimo mensaje de la lead) ==")
for r in sin[:10]:
    print(" -", " | ".join(r))
print("\n== PREGUNTARON PRECIO (nombre | cuando | pregunta | quien respondio | respuesta) ==")
for r in precio[:8]:
    print(" -", " | ".join(r))
print("\n== SEGUIMIENTOS GENERICOS DE ELLA (nombre | cuando | texto) ==")
for r in gen[:6]:
    print(" -", " | ".join(r))
