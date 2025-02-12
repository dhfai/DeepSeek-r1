from config.db_config import get_connection
from utils.input_handler import input_for_accepted

MAIN_MODEL_DEFAULT = "deepseek-r1:latest"
FAST_MODEL_DEFAULT = "deepseek-r1:latest"

def config_model():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model (
            id INT PRIMARY KEY AUTO_INCREMENT,
            active BOOLEAN,
            main_model_source VARCHAR(255),
            fast_model VARCHAR(255)
        )
    """)
    cursor.execute("SELECT * FROM model LIMIT 1")
    row = cursor.fetchone()

    if row is None:
        cursor.execute("INSERT INTO model (active) VALUES (TRUE)")
        conn.commit()
        cursor.execute("SELECT * FROM model LIMIT 1")
        row = cursor.fetchone()

    model_sources = [
        ("main_model_source", "Ollama model path", MAIN_MODEL_DEFAULT),
        ("fast_model", "Fast Ollama model", FAST_MODEL_DEFAULT)
    ]

    for field, title, default in model_sources:
        if row.get(field) is None:
            user_input = input_for_accepted(title, lambda: input(f"(Default: {default}) > ")).strip()
            if not user_input:
                user_input = default
            cursor.execute(f"UPDATE model SET {field} = %s WHERE id = %s", (user_input, row['id']))
            row[field] = user_input

    conn.commit()
    cursor.close()
    conn.close()
    print("Model config is complete")