import sys
import os

# Inserta src/ en el path para poder importar model_module
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(project_root, "src"))


from model_module import main

def cli():
    if len(sys.argv) < 3:
        print("Uso: run_model.py <input_cleaned.xlsx|.csv> <output.xlsx> [<threshold>]")
        sys.exit(1)
    input_file  = sys.argv[1]
    output_file = sys.argv[2]
    threshold   = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    main(input_file, output_file, threshold)

if __name__ == "__main__":
    cli()