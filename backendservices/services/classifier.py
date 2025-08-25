import os 
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from typing import Optional

class TextClassifier:
    def __init__(self, model_path: str = None, threshold: float = 0.85):
        """
        Initializes the classifier with ONNX model and tokenizer.
        """
        if model_path is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            model_path = os.path.join(project_root, "app", "models", "model.onnx")
        self.model_path = model_path

        print(f"🔍 Buscando modelo ONNX en: {self.model_path}")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"ONNX model not found at {model_path}")
        
        self.threshold = threshold
        self.model_path = model_path
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

        self.input_names = {inp.name for inp in self.session.get_inputs()}
        self.output_name = self.session.get_outputs()[0].name

        self.label_map = {
            0: "No observacion",
            1: "observacion"
        }

    def predict(self, text: str) -> str:
        """
        Predict the label for the given text using the ONNX model.
        """
        # Tokenize and prepare input
        inputs = self.tokenizer(text, return_tensors="np", truncation=True, padding='max_length', max_length=256)
        inputs = {k: v.astype(np.int64) for k, v in inputs.items()}
        input_feed = {
            'input_ids': inputs['input_ids'],
            'attention_mask': inputs['attention_mask']
        }

        # Check for models that expect token_type_ids
        if 'token_type_ids' in self.input_names and 'token_type_ids' in inputs:
            input_feed['token_type_ids'] = inputs['token_type_ids']

        # Run inference
        logits = self.session.run([self.output_name], input_feed)[0]

        # Convert logits to probabilities with sigmoid
        probabilities = 1 / (1 + np.exp(-logits))
        predicted_class_id = int(np.argmax(probabilities, axis=1)[0])

        # Apply threshold
        if probabilities[0, predicted_class_id] < self.threshold:
            predicted_class_id = 0  # Default to "Otro" or similar

        return self.label_map.get(predicted_class_id, "Desconocido")
    
