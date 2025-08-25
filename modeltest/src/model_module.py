# src/model_module.py

import os
import pandas as pd
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm
import torch.nn.functional as F

# Configuración de dispositivo: GPU si está disponible, si no, CPU
device = 0 if torch.cuda.is_available() else -1

MODEL_DIR = os.path.join(os.path.dirname(__file__), "../model_output")

# Pipeline con mi modelo
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
classifier = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    return_all_scores=False,   
    device=device,
    batch_size=8               
)

def load_blocks_from_file(input_path: str) -> list[dict]:
    """
    Lee bloques preprocesados desde un .xlsx/.xls o .csv generado por cleaning_module.
    Debe tener columnas 'contenido' y 'page'.
    """
    ext = os.path.splitext(input_path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        df = pd.read_excel(input_path)
    elif ext == ".csv":
        df = pd.read_csv(input_path)
    else:
        raise ValueError(f"Formato no soportado: {ext}. Usa .xlsx, .xls o .csv")
    return df.to_dict(orient="records")

def score_long_paragraph(text):
    # Convierte a IDs sin truncar
    ids = tokenizer(text, add_special_tokens=False)["input_ids"]
    chunk_size = tokenizer.model_max_length
    scores = []
    for i in range(0, len(ids), chunk_size):
        chunk_ids = ids[i : i + chunk_size]
        if len(chunk_ids) < chunk_size:
            chunk_ids = chunk_ids + [tokenizer.pad_token_id] * (chunk_size - len(chunk_ids))
        input_ids = torch.tensor([chunk_ids], device=model.device)  # shape [1,512]
        attention_mask = (input_ids != tokenizer.pad_token_id).long()

        out = model(input_ids=input_ids, attention_mask=attention_mask)
        probs = F.softmax(out.logits, dim=-1)[0]
        scores.append(probs[1].item())
    return max(scores)

def detect_observations(
    blocks: list[dict],
    threshold: float = 0.5
) -> list[dict]:
    """
    Clasifica cada bloque con tu modelo fine-tuned.
    Devuelve solo los que el modelo marca como 'LABEL_1' (observación)
    con score >= threshold y añade el campo 'score'.
    """
    observations = []
    for blk in tqdm(blocks, desc="Clasificando bloques", unit="bloque"):
        text = blk["contenido"].strip()
        if not text:
            continue

        # Si es muy largo, uso chunking
        num_ids = len(tokenizer(text, add_special_tokens=False)["input_ids"])
        score = (
            score_long_paragraph(text)
            if num_ids > tokenizer.model_max_length
            else score_long_paragraph(text)  # podrías reutilizar mismo método
        )

        if score >= threshold:
            blk["score"] = score
            observations.append(blk)
    return observations

def main(
    input_path: str,
    output_path: str = "data/processed/observations_finetuned.xlsx",
    threshold: float = 0.5
):
    # 1) Carga de bloques ya limpios
    blocks = load_blocks_from_file(input_path)
    # 2) Detección con tu modelo fine-tuned
    observations = detect_observations(blocks, threshold)
    # 3) Exportar solo observaciones
    df = pd.DataFrame(observations)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"✅ Observaciones (fine-tuned) guardadas en {output_path} — total: {len(observations)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python model_module.py <input_cleaned.xlsx|.csv> <output.xlsx> [<threshold>]")
        sys.exit(1)
    inp      = sys.argv[1]
    out      = sys.argv[2]
    thr      = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    main(inp, out, thr)
