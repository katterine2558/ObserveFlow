import re 
import unicodedata

_ABBREV_MAP = {
    r"^E(\b|[\s(])": "ELECTRICA",
    r"^S(\b|[\s(])": "ESTRUCTURA",
    r"^B(\b|[\s(])": "GEOTECNIA Y ESTUDIOS GEOMORFOLOGICOS",
    r"^BIM\b": "BIM",
    r"^FADS\b": "FADS",
}

def _strip_accents(speciality: str) -> str:
    return unicodedata.normalize("NFD", speciality).encode("ascii", "ignore").decode("utf-8")

def _clean_basic(speciality: str) -> str:
    # remove quotes/guillements and trailing punctuation noise
    speciality = speciality.replace("«", "").replace("»", "")
    speciality = re.sub(r"[“”\"']", "", speciality)
    speciality = re.sub(r"\s+", " ", speciality).strip()
    return speciality

def normalize_especialidad(name: str):
    """
    Returns (principal_std, sublabel_std, original_clean)
      - principal_std: UPPERCASE, no accents (e.g., 'ELECTRICA')
      - sublabel_std:  UPPERCASE, no accents (e.g., 'LADO AIRE') or None
      - original_clean: cleaned string (keeping accents/case trimmed)

    Rules:
      - Take text before first '(' or ' - ' as principal
      - The part inside '()' (if any) becomes sublabel
      - Remove leading 'DE ' (e.g., 'De Diseño Aeroportuario' -> 'Diseño Aeroportuario')
      - Map abbreviations like 'E (Eléctrica)' -> principal 'ELECTRICA'
      - Uppercase + strip accents for standardized fields
    """
    original = _clean_basic(name)

    # remove '............. 152' 
    original = re.sub(r"\.{2,}\s*\d+\s*$", "", original)

    original = re.sub(r"[–—]", "-", original)

    original = re.sub(r"\s\d+$", "", original)

    # Split principal vs sublabel
    principal, sublabel = original, None


    # A) paréntesis balanceados
    speciality_cleanned = re.match(r"^(.*?)[\s]*\((.+)\)\s*$", principal)
    if speciality_cleanned:
        principal = speciality_cleanned.group(1).strip()
        sublabel = speciality_cleanned.group(2).strip()
    else:
        # (B) paréntesis abiertos sin cerrar: "DE TELECOMUNICACIONES (LADO"
        if "(" in principal and ")" not in principal:
            left, right = principal.split("(", 1)
            principal = left.strip()
            sublabel = re.sub(r"[)\s]+$", "", right.strip()) or None
        else:
            # fallback: ' A - B ' como sublabel
            parts = re.split(r"\s-\s", principal)
            if len(parts) > 1:
                principal, sublabel = parts[0].strip(), " - ".join(parts[1:]).strip()

    # (C) cortar en la primera coma si hay texto oracional: 
    #     "de Señalización Horizontal, es necesario..." -> "de Señalización Horizontal"
    if "," in principal:
        principal = principal.split(",", 1)[0].strip()

    if ";" in principal:
        principal = principal.split(";", 1)[0].strip()

    # Quitar prefijo 'De ' del principal
    principal = re.sub(r"^\s*de\s+", "", principal, flags=re.IGNORECASE)

    # Limpiar colas de puntuación/espacios
    principal = re.sub(r"[,:.\s]+$", "", principal).strip()
    if sublabel:
        sublabel = re.sub(r"[,:.\s]+$", "", sublabel).strip()

    principal_up = principal.upper()

    # (D) ignorar entradas basura como "DE", "DEL", "LA", "EL"
    if principal_up in {"DE", "DEL", "LA", "EL"}:
        return None, None, original  # 👈 señal de “descartar”

    # Abreviaturas
    for pat, repl in _ABBREV_MAP.items():
        if re.match(pat, principal_up):
            principal_up = repl
            break

    # Abreviatura + sublabel -> usa sublabel como principal estándar
    if principal_up in {"E", "S", "B"} and sublabel:
        override = _strip_accents(sublabel).upper()
        principal_up = re.sub(r"\s+", " ", override).strip()

    principal_std = re.sub(r"\s+", " ", _strip_accents(principal_up)).strip().upper()
    sublabel_std = None
    if sublabel:
        sublabel_std = re.sub(r"\s+", " ", _strip_accents(sublabel)).strip().upper()

    return principal_std, sublabel_std, original