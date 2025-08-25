from bisect import bisect_right
from typing import List, Dict, Optional

def _prepare_occurrences(especialidades: List[Dict]) -> List[Dict]:
    """
    - Quita entradas sin especialidad_std
    - Ordena por página
    - Deduplica duplicados contiguos exactos (misma página + mismo std + mismo sublabel)
    """
    cleaned = []
    for especialidad in especialidades:
        principal = especialidad.get("especialidad_std")
        if not principal:
            continue
        cleaned.append({
            "pagina": int(especialidad["pagina"]),
            "especialidad_std": principal,
            "sublabel_std": especialidad.get("sublabel_std") or None,
        })
    cleaned.sort(key=lambda x: x["pagina"])

    dedup = []
    
    for especialidad in cleaned:
        if not dedup:
            dedup.append(especialidad)
        else:
            last = dedup[-1]
            if not (last["pagina"] == especialidad["pagina"] and
                    last["especialidad_std"] == especialidad["especialidad_std"] and
                    (last["sublabel_std"] or None) == (especialidad["sublabel_std"] or None)):
                dedup.append(especialidad)
    return dedup

def asignar_especialidad(pagina_obs: int, especialidades: List[Dict]) -> str:
    """
    Devuelve la especialidad principal estandarizada (string).
    Toma la última ocurrencia cuya página <= pagina_obs.
    """
    occ = _prepare_occurrences(especialidades)
    if not occ:
        return "DESCONOCIDA"

    pages = [e["pagina"] for e in occ]
    idx = bisect_right(pages, int(pagina_obs)) - 1
    if idx < 0:
        return "DESCONOCIDA"

    return occ[idx]["especialidad_std"]

def asignar_especialidad_ext(pagina_obs: int, especialidades: List[Dict]) -> Dict[str, Optional[str]]:
    """
    Versión extendida: devuelve principal y sublabel (si existe).
    Ejemplo: {"principal": "ELECTRICA", "sublabel": "LADO AIRE"}
    """
    occ = _prepare_occurrences(especialidades)
    if not occ:
        return {"principal": "DESCONOCIDA", "sublabel": None}

    pages = [e["pagina"] for e in occ]
    idx = bisect_right(pages, int(pagina_obs)) - 1
    if idx < 0:
        return {"principal": "DESCONOCIDA", "sublabel": None}

    hit = occ[idx]
    return {"principal": hit["especialidad_std"], "sublabel": hit.get("sublabel_std")}
