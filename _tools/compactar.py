#!/usr/bin/env python3
"""
Reduce un resultado crudo del conector High_Level a los campos compactos de la
seccion 3 de la rutina. El crudo se guarda en archivo por el sistema; aqui se
lee de disco, se extrae solo lo que usa gestion_semanal.py y se escribe el
compacto en la carpeta de la clienta. Nunca pasa por el contexto.

Uso: compactar.py <contactos|mensajes|citas> <crudo.json> <salida.json> [--append]

Imprime solo conteos.
"""
import json
import sys


def cargar(ruta):
    with open(ruta) as f:
        txt = f.read().strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # algunos volcados vienen como JSONL o con basura alrededor del JSON
        ini = min([i for i in (txt.find("{"), txt.find("[")) if i != -1])
        return json.loads(txt[ini:])


def desanidar(d, llaves):
    """Busca la primera lista util dentro de una respuesta anidada."""
    if isinstance(d, list):
        return d
    if not isinstance(d, dict):
        return []
    for k in llaves:
        if isinstance(d.get(k), list):
            return d[k]
    for k in ("data", "result", "response", "body", "content"):
        if k in d:
            sub = desanidar(d[k], llaves)
            if sub:
                return sub
    # ultimo recurso: la lista de diccionarios mas larga del arbol
    mejor = []
    for v in d.values():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            if len(v) > len(mejor):
                mejor = v
        elif isinstance(v, dict):
            sub = desanidar(v, llaves)
            if len(sub) > len(mejor):
                mejor = sub
    return mejor


CAMPOS = {
    "contactos": (
        ["contacts", "contact"],
        ["id", "dateAdded", "tags", "attributionSource", "lastAttributionSource",
         "firstName", "contactName"],
    ),
    "mensajes": (
        ["messages", "message"],
        ["contactId", "direction", "body", "userId", "from", "dateAdded",
         "attachments"],
    ),
    "citas": (
        ["events", "appointments", "calendarEvents"],
        ["id", "contactId", "dateAdded", "startTime", "createdBy",
         "appointmentStatus", "deleted"],
    ),
}


def main():
    tipo, crudo, salida = sys.argv[1], sys.argv[2], sys.argv[3]
    append = "--append" in sys.argv
    llaves, campos = CAMPOS[tipo]

    filas = desanidar(cargar(crudo), llaves)
    nuevos = [{c: f.get(c) for c in campos if c in f} for f in filas
              if isinstance(f, dict)]

    previos = []
    if append:
        try:
            previos = json.load(open(salida))
        except (OSError, json.JSONDecodeError):
            previos = []

    todo = previos + nuevos
    if tipo == "citas":
        # dedup por id, tal como pide la seccion 3.3
        vistos, unicos = set(), []
        for c in todo:
            k = c.get("id")
            if k is not None and k in vistos:
                continue
            if k is not None:
                vistos.add(k)
            unicos.append(c)
        todo = unicos

    json.dump(todo, open(salida, "w"), ensure_ascii=False)
    print(f"{tipo}: +{len(nuevos)} nuevos, {len(todo)} en total -> {salida}")


if __name__ == "__main__":
    main()
