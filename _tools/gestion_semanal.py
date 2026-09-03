#!/usr/bin/env python3
"""
Mide la gestion de una clienta sobre sus leads de anuncio, dos semanas de una vez.

Este archivo es la UNICA definicion de "lead de anuncio", "mensaje de ella" y
"cita". El documento de la clienta y el triage leen los dos de aqui, para que no
puedan decir numeros distintos sobre la misma persona.

Entradas (JSON crudo, tal como vuelve de la API):
  --contactos  search-contacts-advanced de los ultimos 14 dias (sin filtrar)
  --mensajes   export-messages-by-location, todas las paginas, sin filtro de canal
  --citas      get-calendar-events

  --fin        domingo de la semana que se reporta (YYYY-MM-DD)

Salida: los mismos conteos para la semana reportada y la anterior.

QUE CUENTA COMO QUE (verificado en vivo, 31 ago 2026):

  Lead de anuncio = contacto creado en la semana que cumple AL MENOS UNA:
      - lleva fb-ad-lead-whatsapp, instagram-ad-lead-whatsapp o lead_ads
      - su atribucion trae adId, o un sessionSource que empieza por "Paid"
    Es union: las dos fuentes fallan en cuentas distintas, casi nunca en la misma.
    Lo que no cumple ninguna se cuenta como lead propio de ella (organico).

  Mensaje de ella = saliente que cumple AL MENOS UNA:
      - el body trae el marcador "Sent from another device"  (su telefono)
      - tiene userId, el que sea                             (ella o su equipo)
    Cualquier otro saliente va a "no atribuido" y NO se le acredita.
    Se probo apoyarse en `from` y en `source` y ninguno sirve: en la cuenta de
    May Garcia el `from` saliente es la palabra "Whatsapp" y el `source` es "api"
    tanto para ella como para el bot. Por eso el numero de gestion es un PISO:
    puede quedarse corto, nunca inflado.

  Tasa de agendamiento = leads_que_agendaron / leads_de_anuncio. Es el numero
    principal. No necesita cohorte madurada: medido sobre 25 agendamientos
    reales de dos cuentas, la mediana entre que llega el lead y que agenda es
    de 18 MINUTOS y el 92% agenda dentro de 24 horas, asi que una ventana de
    lunes a domingo se queda corta en ~1%.

  Quien agendo = quien PARTICIPO antes de la cita, no quien la creo. Regla
    simetrica: si los dos pusieron algo, es esfuerzo mutuo.
      Ella participo  = escribio antes de la cita (con margen) O creo la cita
                        ella misma (createdBy.userId poblado).
      El bot participo = hubo saliente no atribuible antes de la cita O la cita
                        la creo conversations_ai.
      los dos -> esfuerzo_mutuo | solo ella -> ella | solo el bot -> el_bot_sola
      ninguno -> se_agendo_la_lead_sola (un enlace, sin conversacion)
    Se cuenta la PRIMERA cita del lead: es la que lo convirtio.

    Se mira participacion y no autoria porque la autoria miente en los dos
    sentidos: el bot puede llevar la conversacion entera y ella solo pulsar
    "agendar" (caso real: 8 mensajes del bot contra 1 suyo), y ella puede
    cerrar por telefono y agendar a mano sin escribir una linea.

    Verificado en vivo (31 ago 2026, 108 citas de Gloribel Gonzalez):
    conversations_ai y booking_widget vienen SIEMPRE con userId null;
    mobile_app, calendar_page y contactdetails_page vienen SIEMPRE con userId.
    Por eso la autoria se ancla en userId y no en una lista de `source`: los
    nombres de origen cambian, la presencia del userId no.

    Ojo: los salientes de ella que no llevan firma (por ejemplo Instagram, que
    no trae userId) cuentan como "el bot participo". Eso mueve credito de
    "ella" hacia "esfuerzo mutuo", nunca al reves: sigue siendo un piso.

  Nota de voz / foto = por la extension de la URL del adjunto, o por el body
    ">AUDIO<" / ">IMAGE<". `contentType` NO sirve: viene "text/plain" incluso en
    mensajes con foto. Los adjuntos que no se pueden clasificar se cuentan aparte.
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HUSO = ZoneInfo("America/New_York")
TAGS_ANUNCIO = {"fb-ad-lead-whatsapp", "instagram-ad-lead-whatsapp", "lead_ads"}
AUDIO_EXT = (".ogg", ".mp3", ".m4a", ".amr", ".opus", ".aac")
IMAGEN_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".gif")
MARCA_TELEFONO = "sent from another device"

# Un mensaje en el mismo minuto del agendamiento es simultaneo, no es lo que lo
# produjo. Caso real: en la cuenta de May Garcia el bot
# llevo una conversacion entera y ella solto un "Perchero" UN SEGUNDO antes de
# la confirmacion; sin este margen contaria como que ella intervino. Son los
# mismos 120s que usa el deduplicador, por la misma razon.
MARGEN_INTERVENCION = timedelta(seconds=120)


def ts(valor):
    if not valor:
        return None
    v = str(valor).replace("Z", "+00:00")
    try:
        d = datetime.fromisoformat(v)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def semana(domingo, atras=0):
    """Lunes 00:00 a domingo 23:59:59 en America/New_York, devuelto en UTC."""
    d = datetime.strptime(domingo, "%Y-%m-%d").date() - timedelta(days=7 * atras)
    lunes = d - timedelta(days=6)
    ini = datetime.combine(lunes, datetime.min.time(), tzinfo=HUSO)
    fin = datetime.combine(d, datetime.max.time(), tzinfo=HUSO)
    return ini.astimezone(timezone.utc), fin.astimezone(timezone.utc)


def es_lead_de_anuncio(c):
    tags = {str(t).lower().strip() for t in (c.get("tags") or [])}
    if TAGS_ANUNCIO & tags:
        return True
    for k in ("attributionSource", "lastAttributionSource"):
        a = c.get(k) or {}
        if a.get("adId"):
            return True
        if str(a.get("sessionSource") or "").lower().startswith("paid"):
            return True
    return False


def limpiar(body):
    b = re.sub(r"🔁?\s*Sent from another device.*?🔁?", "", body or "", flags=re.I | re.S)
    return re.sub(r"\s+", " ", b).strip().lower()


def urls(m):
    return [str(a).split("?")[0].lower() for a in (m.get("attachments") or [])]


def es_audio(m):
    return (any(u.endswith(AUDIO_EXT) for u in urls(m))
            or (m.get("body") or "").strip() == ">AUDIO<")


def es_imagen(m):
    return (any(u.endswith(IMAGEN_EXT) for u in urls(m))
            or (m.get("body") or "").strip() in (">IMAGE<", ">IMG<"))


def sin_clasificar(m):
    return [u for u in urls(m)
            if not u.endswith(AUDIO_EXT) and not u.endswith(IMAGEN_EXT)]


def es_de_ella(m):
    if MARCA_TELEFONO in (m.get("body") or "").lower():
        return True
    return bool((m.get("userId") or "").strip())


def deduplicar(mensajes):
    """Colapsa el eco de WhatsApp: el mismo saliente aparece dos veces (mismo
    contacto, mismo cuerpo y adjuntos, menos de 2 minutos). Se conserva la copia
    con mas senal (marcador > userId > resto). No se ancla en `from`: esta
    verificado que en algunas cuentas `from` es la palabra "Whatsapp" para todo.
    Donde no hay eco no colapsa nada.
    """
    def senal(m):
        if MARCA_TELEFONO in (m.get("body") or "").lower():
            return 2
        return 1 if (m.get("userId") or "").strip() else 0

    grupos = defaultdict(list)
    otros = []
    for m in mensajes:
        t = ts(m.get("dateAdded"))
        if m.get("direction") == "outbound" and t:
            m["_t0"] = t
            grupos[(m.get("contactId"), limpiar(m.get("body")), tuple(urls(m)))].append(m)
        else:
            otros.append(m)

    limpios, ecos = list(otros), 0
    for lista in grupos.values():
        lista.sort(key=lambda m: m["_t0"])
        bloque = []
        for m in lista:
            if bloque and (m["_t0"] - bloque[-1]["_t0"]).total_seconds() > 120:
                limpios.append(max(bloque, key=senal))
                ecos += len(bloque) - 1
                bloque = []
            bloque.append(m)
        if bloque:
            limpios.append(max(bloque, key=senal))
            ecos += len(bloque) - 1
    return limpios, ecos


def reparto(partes, total):
    """Porcentajes enteros sobre `total` que suman EXACTAMENTE el porcentaje del
    conjunto. Redondeando cada cubo por su cuenta, 12 + 5 + 3 puede no dar 20 y
    el desglose parece roto; aqui el resto se reparte por resto mayor.
    Devuelve (porcentaje_del_conjunto, {cubo: porcentaje}) o None si no hay base.
    """
    if not total:
        return None
    objetivo = round(100 * sum(partes.values()) / total)
    crudo = {k: 100 * v / total for k, v in partes.items()}
    ent = {k: int(v) for k, v in crudo.items()}
    orden = sorted(crudo, key=lambda k: crudo[k] - ent[k], reverse=True)
    resto = objetivo - sum(ent.values())
    while resto > 0:
        for k in orden:
            if resto == 0:
                break
            ent[k] += 1
            resto -= 1
    while resto < 0:
        for k in reversed(orden):
            if resto == 0:
                break
            if ent[k] > 0:
                ent[k] -= 1
                resto += 1
    return objetivo, ent


def medir(contactos, mensajes, citas, ini, fin):
    leads, propios = set(), 0
    for c in contactos:
        t = ts(c.get("dateAdded"))
        if not t or not (ini <= t <= fin):
            continue
        if es_lead_de_anuncio(c):
            leads.add(c.get("id"))
        else:
            propios += 1

    # Solo mensajes hasta el domingo de ESTA semana: las dos cohortes se miden
    # con la misma maduracion (0-7 dias) y la comparacion es valida. Sin limite
    # inferior: la conversacion pudo empezar hasta 3 dias antes del contacto.
    por_contacto = defaultdict(list)
    sin_firma_por_contacto = defaultdict(list)
    no_atribuidos = adj_raros = 0
    for m in mensajes:
        cid, t = m.get("contactId"), ts(m.get("dateAdded"))
        if cid not in leads or not t or t > fin:
            continue
        if m.get("direction") == "inbound":
            continue
        if es_de_ella(m):
            m["_t"] = t
            adj_raros += len(sin_clasificar(m))
            por_contacto[cid].append(m)
        else:
            no_atribuidos += 1
            sin_firma_por_contacto[cid].append(t)

    citas_lead, citas_ajenas = defaultdict(list), 0
    for c in citas:
        cid, creada = c.get("contactId"), ts(c.get("dateAdded"))
        if not creada or not (ini <= creada <= fin) or c.get("deleted"):
            continue
        if cid in leads:
            citas_lead[cid].append(c)
        else:
            citas_ajenas += 1

    origen = defaultdict(int)
    for lista in citas_lead.values():
        for c in lista:
            origen[(c.get("createdBy") or {}).get("source") or "sin_dato"] += 1

    gest_antes = voz = gest_despues = foto = 0
    agendo_ella = bot_sola = mutuo = agendo_la_lead = 0
    for lid in leads:
        suyos = sorted(por_contacto.get(lid, []), key=lambda m: m["_t"])
        cs = sorted(citas_lead.get(lid, []), key=lambda c: ts(c.get("dateAdded")))

        corte = ts(cs[0].get("dateAdded")) if cs else None
        antes = [m for m in suyos if not corte or m["_t"] < corte]
        if antes:
            gest_antes += 1
        if any(es_audio(m) for m in antes):
            voz += 1

        despues = []
        for c in cs:
            t0, t1 = ts(c.get("dateAdded")), ts(c.get("startTime"))
            despues += [m for m in suyos
                        if t0 and m["_t"] > t0 and (not t1 or m["_t"] < t1)]
        if despues:
            gest_despues += 1
        if any(es_imagen(m) for m in despues):
            foto += 1

        # Quien agendo a este lead: quien PARTICIPO antes de la PRIMERA cita,
        # que es la que lo convirtio. Si despues cancela y alguien reagenda,
        # eso no borra quien hizo el trabajo que cerro.
        if cs:
            creada_por = (cs[0].get("createdBy") or {})
            limite = corte - MARGEN_INTERVENCION
            puso_ella = (any(m["_t"] < limite for m in antes)
                         or bool((creada_por.get("userId") or "").strip()))
            puso_bot = (any(t < limite for t in sin_firma_por_contacto.get(lid, []))
                        or creada_por.get("source") == "conversations_ai")
            if puso_ella and puso_bot:
                mutuo += 1
            elif puso_ella:
                agendo_ella += 1
            elif puso_bot:
                bot_sola += 1
            else:
                agendo_la_lead += 1

    quien = {
        "el_bot_sola": bot_sola,
        "ella": agendo_ella,
        "esfuerzo_mutuo": mutuo,
        "se_agendo_la_lead_sola": agendo_la_lead,
    }
    # Todo sobre el mismo denominador: los leads. Asi los cuatro cubos suman la
    # tasa de agendamiento y el desglose explica el numero principal en vez de
    # vivir aparte. Sin leads no hay tasa: None, nunca 0%.
    r = reparto(quien, len(leads))
    pct = None if r is None else dict({"agendamiento": r[0]}, **r[1])

    return {
        "desde": ini.astimezone(HUSO).strftime("%Y-%m-%d"),
        "hasta": fin.astimezone(HUSO).strftime("%Y-%m-%d"),
        "leads_de_anuncio": len(leads),
        "gestionados_antes_de_agendar": gest_antes,
        "con_nota_de_voz": voz,
        "leads_que_agendaron": len(citas_lead),
        "quien_agendo": quien,
        "porcentajes_sobre_leads": pct,
        "gestionados_despues_de_agendar": gest_despues,
        "con_foto": foto,
        "citas_por_origen": dict(origen),
        "aparte": {
            "leads_propios_de_ella": propios,
            "citas_de_contactos_que_no_son_leads": citas_ajenas,
        },
        "calidad_del_dato": {
            "salientes_no_atribuibles": no_atribuidos,
            "leads_sin_ningun_mensaje_de_ella": len(leads) - len(por_contacto),
            "adjuntos_sin_extension": adj_raros,
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--contactos", required=True)
    p.add_argument("--mensajes", required=True)
    p.add_argument("--citas", required=True)
    p.add_argument("--fin", required=True, help="domingo de la semana reportada, YYYY-MM-DD")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    contactos = json.load(open(a.contactos))
    mensajes = json.load(open(a.mensajes))
    citas = json.load(open(a.citas))
    mensajes, ecos = deduplicar(mensajes)

    # Cuantos salientes de TODA la cuenta (leads o no) llevan firma de ella
    # (marcador o userId). Si es 0, ella es invisible para nosotros en esa
    # cuenta y un "0 gestionados" NO es un dato: es que no podemos medirla.
    firmados = sum(1 for m in mensajes
                   if m.get("direction") == "outbound" and es_de_ella(m))

    resumen = {
        "semana": medir(contactos, mensajes, citas, *semana(a.fin, 0)),
        "semana_anterior": medir(contactos, mensajes, citas, *semana(a.fin, 1)),
        "salientes_con_firma_en_toda_la_cuenta": firmados,
        "ecos_deduplicados": ecos,
    }
    json.dump(resumen, open(a.out, "w"), ensure_ascii=False, indent=2)
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
