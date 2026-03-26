import os 
from db import get_connection

files = os.listdir("data/raw")
print(files)

conn = get_connection()
# What we use to execut the SQL statements 
cur = conn.cursor() 

# Loop through files and execute insert for each 
for file in files:
    # cur.execute(SQL Query, params)
    cur.execute( 
        "INSERT INTO receipt (file_name) VALUES (%s) ON CONFLICT DO NOTHING",
        (file,)
    )

conn.commit()
cur.close()
conn.close()
