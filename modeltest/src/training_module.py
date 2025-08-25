import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)

def load_labeled_dataset(path: str) -> Dataset:
    """
    Carga un CSV etiquetado con columnas 'contenido' y 'label' (0 o 1).
    Devuelve un Hugging Face Dataset con columnas 'text' y 'label'.
    """
    df = pd.read_csv(path, sep=';')
    df = df.rename(columns={'contenido': 'text'})
    df['label'] = df['label'].astype(int)
    return Dataset.from_pandas(df[['text', 'label']])

def preprocess(dataset: Dataset, tokenizer, max_length: int = 256) -> Dataset:
    """
    Tokeniza el dataset para el modelo.
    """
    def tokenize_fn(examples):
        return tokenizer(
            examples['text'],
            padding='max_length',
            truncation=True,
            max_length=max_length
        )
    return dataset.map(tokenize_fn, batched=True)

def compute_metrics(eval_pred):
    """
    Calcula accuracy.
    """
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = (preds == labels).astype(np.float32).mean().item()
    return {'accuracy': acc}

def main(
    labeled_csv: str,
    model_name: str = "distilbert-base-multilingual-cased",
    output_dir: str = "model_output",
    num_train_epochs: int = 3,
    train_batch_size: int = 8,
    eval_batch_size: int = 8,
    learning_rate: float = 5e-5
):
    # 1. Carga y partición
    dataset = load_labeled_dataset(labeled_csv)
    train_ds, eval_ds = train_test_split(dataset.to_pandas(), test_size=0.2, random_state=42, stratify=dataset['label'])
    train_ds = Dataset.from_pandas(train_ds)
    eval_ds = Dataset.from_pandas(eval_ds)

    # 2. Tokenizador y modelo
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_ds = preprocess(train_ds, tokenizer)
    eval_ds = preprocess(eval_ds, tokenizer)
    train_ds.set_format(type='torch', columns=['input_ids','attention_mask','label'])
    eval_ds.set_format(type='torch', columns=['input_ids','attention_mask','label'])

    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

    # 3. Argumentos
    args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size=eval_batch_size,
        logging_dir=f"{output_dir}/logs",
        logging_steps=50,
        # En lugar de evaluation_strategy="epoch":
        do_eval=True,
        # En lugar de save_strategy="epoch":
        save_steps=500,           # guarda cada 500 pasos (ajusta según tu dataset)
        save_total_limit=1        # conserva solo el último checkpoint
    )

    # 4. Trainer
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    # 5. Entrenamiento
    trainer.train()

    # 6. Guardar
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"✅ Modelo entrenado y guardado en {output_dir}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python training_module.py <labeled.csv> [model_name] [output_dir] [epochs] [train_bs] [eval_bs] [lr]")
        sys.exit(1)
    labeled_csv  = sys.argv[1]
    model_name   = sys.argv[2] if len(sys.argv)>2 else "distilbert-base-multilingual-cased"
    output_dir   = sys.argv[3] if len(sys.argv)>3 else "model_output"
    epochs       = int(sys.argv[4]) if len(sys.argv)>4 else 3
    train_bs     = int(sys.argv[5]) if len(sys.argv)>5 else 8
    eval_bs      = int(sys.argv[6]) if len(sys.argv)>6 else 8
    lr           = float(sys.argv[7]) if len(sys.argv)>7 else 5e-5
    main(labeled_csv, model_name, output_dir, epochs, train_bs, eval_bs, lr)

