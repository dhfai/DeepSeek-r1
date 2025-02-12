import shutil
import re
from config.db_config import get_connection

MODELFILE_TEMPLATE = "Modelfile-template"
MODELFILE_GENERATED = "Modelfile-generated"


def write_modelfile():
    print("Creating Modelfile for Ollama...")
    shutil.copy(MODELFILE_TEMPLATE, MODELFILE_GENERATED)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM agent LIMIT 1")
    agent = cursor.fetchone()
    cursor.execute("SELECT * FROM model LIMIT 1")
    model = cursor.fetchone()
    conn.close()

    mapper = {
        "agent_type": agent["agent_type"],
        "agent_name": agent["agent_name"],
        "agent_relation": agent["agent_relation"],
        "agent_attitude": agent["agent_attitude"],
        "user_name": agent["user_name"],
        "main_model_source": model["main_model_source"]
    }

    with open(MODELFILE_GENERATED, 'r') as file:
        contents = file.read()
        for key, value in mapper.items():
            contents = re.sub(f"\\[{key}\\]", value, contents)

    with open(MODELFILE_GENERATED, 'w') as file:
        file.write(contents)