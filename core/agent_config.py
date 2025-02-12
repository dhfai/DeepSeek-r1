from config.db_config import get_connection
from utils.input_handler import input_for_accepted

def config_agent():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent (
            id INT PRIMARY KEY AUTO_INCREMENT,
            active BOOLEAN,
            agent_type VARCHAR(255),
            agent_name VARCHAR(255),
            agent_relation VARCHAR(255),
            agent_attitude TEXT,
            user_name VARCHAR(255)
        )
    """)
    cursor.execute("SELECT * FROM agent LIMIT 1")
    row = cursor.fetchone()

    if row is None:
        cursor.execute("INSERT INTO agent (active) VALUES (TRUE)")
        conn.commit()
        cursor.execute("SELECT * FROM agent LIMIT 1")
        row = cursor.fetchone()

    fields = [
        ("agent_type", "Chatbot agent type/description", "E.g. 'a research assistant'\n> The chatbot agent is... "),
        ("agent_name", "Agent name", "> Name: "),
        ("agent_relation", "Agent relation", "E.g. 'your supervisor'\n> I am... "),
        ("agent_attitude", "Agent attitude", "E.g. 'researches new topics and discusses existing research.'\n> Agent attitude: "),
        ("user_name", "Your name", "> Name: ")
    ]

    for field, prompt_title, prompt in fields:
        if row.get(field) is None:
            user_input = input_for_accepted(prompt_title, lambda: input(prompt))
            cursor.execute(f"UPDATE agent SET {field} = %s WHERE id = %s", (user_input, row['id']))
            row[field] = user_input

    conn.commit()
    cursor.close()
    conn.close()
    print("Agent config is complete")
