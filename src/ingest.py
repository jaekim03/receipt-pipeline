import os
from db import get_connection

script_dir = os.path.dirname(os.path.abspath(__file__))
raw_dir = os.path.join(script_dir, "..", "data", "raw")

files = os.listdir(raw_dir)
print(files)

conn = get_connection()
cur = conn.cursor()

for file in files:
    cur.execute(
        "INSERT INTO receipt (file_name) VALUES (%s) ON CONFLICT DO NOTHING",
        (file,)
    )

conn.commit()
cur.close()
conn.close()
