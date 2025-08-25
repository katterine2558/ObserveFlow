import openpyxl as px

def excel_observation_cheker(excel_path: str, texts: list[str]) -> set[str]:
    """
    Inserta en bloque los textos en la columna G de 'Matriz Obs' desde la fila 13.
    Devuelve un set con los textos NORMALIZADOS que fueron agregados (no existentes previamente).
    """
    SHEET_NAME = "Matriz Obs"
    COL = 7
    START_ROW = 13

    def _norm(s: str) -> str:
        return (s or "").strip()

    def _first_empty_row(ws, col=COL, start=START_ROW):
        mr = ws.max_row
        if mr < start:
            return start
        r = mr
        while r >= start:
            v = ws.cell(row=r, column=col).value
            if v is not None and str(v).strip() != "":
                return r + 1
            r -= 1
        return start

    if not texts:
        return set()

    #Abre el excel
    wb = px.load_workbook(filename=excel_path, data_only=True, read_only=False)
    ws = wb[SHEET_NAME]

    # Observaciones ya existentes
    existentes = {
        _norm(v)
        for (v,) in ws.iter_rows(
            min_row=START_ROW,
            max_row=ws.max_row,
            min_col=COL,
            max_col=COL,
            values_only=True
        )
        if v not in (None, "")
    }

    # Filtra textos nuevos
    vistos = set()
    to_add = []
    for t in texts:
        tn = _norm(t)
        if not tn or tn in existentes or tn in vistos:
            continue
        to_add.append(t)
        vistos.add(tn)

    agregados = set()
    if to_add:
        row = _first_empty_row(ws, COL, START_ROW)
        for t in to_add:
            ws.cell(row=row, column=COL, value=t)
            agregados.add(_norm(t))
            row += 1
        wb.save(excel_path)

    wb.close()
    return agregados
