import sys, os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(project_root, "src"))

from training_module import main

def cli():
    if len(sys.argv) < 2:
        print("Uso: run_training.py <labeled.csv> [model_name] [output_dir] [epochs] [train_bs] [eval_bs] [lr]")
        sys.exit(1)
    main(*sys.argv[1:])

if __name__ == "__main__":
    cli()