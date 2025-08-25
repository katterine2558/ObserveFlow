Overview

This project provides a complete pipeline to process technical PDF reports and automatically detect, classify, and map observations into their corresponding Excel “Matriz de Observaciones”.

It combines two main components:

Flask API – Receives a PDF and multiple Excel files, extracts paragraphs, classifies them (observation vs. non-observation), assigns them to the correct specialty, and updates the corresponding Excel sheets.

Training & CLI pipeline – Custom training and inference scripts for fine-tuning a Transformer model (DistilBERT multilingual) and applying it to cleaned PDF blocks.
