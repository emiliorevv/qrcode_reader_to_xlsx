# parser_qr.py
import json
import re
import unicodedata

# Conjuntos base (usados junto con detectores por substring)
NOMBRE_KEYS = {"nombre", "name"}
AREA_KEYS   = {"area", "área", "departamento", "dept", "depto", "division", "división"}

def _preclean_key(s: str) -> str:
    """Minúsculas, sin acentos y mapea N°/Nº/No. -> 'no' para que se detecte."""
    s = s.strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")  # quita acentos
    s = s.replace("n°", "no").replace("nº", "no").replace("no.", "no")
    return s

def _normalize_key(s: str) -> str:
    """Versión colapsada (solo letras/dígitos) para comparar tokens."""
    s = _preclean_key(s)
    s = re.sub(r"[^a-z0-9]", "", s)
    return s

def _is_name_key(orig_key: str, norm_key: str) -> bool:
    pre = _preclean_key(orig_key)
    # por sinónimos exactos o porque contiene 'nombre'/'name'
    return (norm_key in {"nombre", "name"}) or ("nombre" in pre) or ("name" in pre)

def _is_area_key(orig_key: str, norm_key: str) -> bool:
    pre = _preclean_key(orig_key)
    # acepta 'area' por substring y sinónimos comunes
    return (
            "area" in pre
            or "depart" in pre      # departamento, dept, depto
            or "dept" in pre
            or "depto" in pre
            or "division" in pre
            or norm_key in {"area", "departamento", "dept", "depto", "division"}
    )

def _looks_like_employee_number_key(orig_key: str, norm_key: str) -> bool:
    """
    Detecta muchas variantes del número de empleado:
      - contiene 'emplead' + (numero|num|no|nro|id|codigo|clave|legajo|matricula)
      - compactos: numerodeempleado, idempleado, etc.
    """
    pre = _preclean_key(orig_key)
    has_empleado = ("emplead" in norm_key) or ("emplead" in pre.replace(" ", ""))
    tokens = ["numero", "num", "no", "nro", "id", "codigo", "clave", "legajo", "matricula"]
    has_token = any(t in pre for t in tokens) or any(t in norm_key for t in tokens)
    compact_hits = {
        "numeroempleado","numerodeempleado","numempleado","noempleado","nroempleado",
        "idempleado","codigoempleado","claveempleado","legajo","matricula"
    }
    return (has_empleado and has_token) or (norm_key in compact_hits)

def _is_pure_number(s: str) -> bool:
    return bool(re.fullmatch(r"\d+", s.strip()))

def _try_json(text: str):
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return None

def _kv_candidates(text: str):
    """
    Genera pares (clave, valor) priorizando formatos en una sola línea como:
    'Nombre: Zuka, N° de empleado: 23130705, Area: Linea de produccion'
    También soporta ';' y '=' y multilínea.
    """
    pairs = []

    # ---- 1) partir todo el texto en "trozos" por ';' o ',' ----
    flat = text.replace("\n", " ")
    chunks = []
    tmp = [p.strip() for p in flat.split(";")]
    for part in tmp:
        chunks.extend([c.strip() for c in part.split(",")])

    # de cada trozo intenta k=v o k: v
    for chunk in chunks:
        if not chunk:
            continue
        if "=" in chunk:
            k, v = chunk.split("=", 1)
            k, v = k.strip(), v.strip()
            if k and v:
                pairs.append((k, v))
            continue
        if ":" in chunk:
            k, v = chunk.split(":", 1)
            k, v = k.strip(), v.strip()
            if k and v:
                pairs.append((k, v))
            continue

    if pairs:
        return pairs

    # ---- 2) Fallback: procesar por líneas con ':' o '-' ----
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            pairs.append((k.strip(), v.strip()))
            continue
        if "-" in line and re.match(r"^[A-Za-zÁÉÍÓÚÜáéíóúüñÑ #.]+-\s*", line):
            k, v = re.split(r"\s*-\s*", line, maxsplit=1)
            pairs.append((k.strip(), v.strip()))

    return pairs

def extract_employee_fields(raw_text: str):
    """
    Devuelve dict con columnas exactas:
      {"Nombre": str, "Número de empleado": str, "Área": str}
    Si falta algo, (None, "mensaje de error").
    """
    nombre = numero = area = None

    # 1) JSON directo
    data = _try_json(raw_text)
    if isinstance(data, dict):
        for k, v in data.items():
            norm = _normalize_key(str(k))
            if not nombre and _is_name_key(k, norm):
                nombre = str(v).strip()
            elif not numero and _looks_like_employee_number_key(k, norm):
                numero = str(v).strip()
            elif not area and _is_area_key(k, norm):
                area = str(v).strip()

    # 2) Pares clave-valor
    if not (nombre and numero and area):
        for k, v in _kv_candidates(raw_text):
            norm = _normalize_key(k)
            if not nombre and _is_name_key(k, norm):
                nombre = v.strip()
                continue
            if not area and _is_area_key(k, norm):
                area = v.strip()
                continue
            if not numero and (_looks_like_employee_number_key(k, norm) or norm == "empleado"):
                vv = v.strip()
                if norm != "empleado" or _is_pure_number(vv):
                    numero = vv
                    continue

    # 3) Limpieza y validación final
    def clean(x):
        return x.strip() if isinstance(x, str) else x
    nombre, numero, area = clean(nombre), clean(numero), clean(area)

    missing = []
    if not nombre: missing.append("Nombre")
    if not numero: missing.append("Número de empleado")
    if not area:   missing.append("Área")

    if missing:
        return None, f"Faltan campos: {', '.join(missing)}"
    return {"Nombre": nombre, "Número de empleado": numero, "Área": area}, None
