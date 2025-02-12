#!/bin/bash

read -p "This will delete all configurations, modelfile, and reset database tables. Are you sure? (y/n): " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    if [ -f "Modelfile-generated" ]; then
        rm Modelfile-generated
        echo "✅ Deleted generated Modelfile."
    else
        echo "ℹ️ Modelfile-generated does not exist."
    fi

    if [ -d "chroma_db_mem" ]; then
        rm -rf chroma_db_mem
        echo "✅ Deleted conversation memory."
    else
        echo "ℹ️ No conversation memory found."
    fi

    python3 << EOF
from config.db_config import get_connection

try:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM agent")
    cursor.execute("DELETE FROM model")
    conn.commit()

    print("✅ Cleared database tables: agent and model.")

except Exception as e:
    print(f"❌ Database reset failed: {e}")

finally:
    cursor.close()
    conn.close()
EOF

    echo "✅ System reset complete."
else
    echo "❌ Reset aborted."
fi
