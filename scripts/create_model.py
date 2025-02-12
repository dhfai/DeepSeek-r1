import subprocess

MAIN_MODEL_NAME = "deepseek-guru"
MODELFILE_GENERATED = "Modelfile-generated"


def create_model():
    print("Creating model from Modelfile using Ollama...")
    subprocess.check_output(f"ollama create {MAIN_MODEL_NAME} -f {MODELFILE_GENERATED}", shell=True)
