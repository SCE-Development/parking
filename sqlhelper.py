import sqlite3
from datetime import datetime, timedelta    

#database setup function
def create_table(dbfile: str, garage_data):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    
    for garage_name in garage_data.keys():
        table_name = garage_name.replace(" ", "_")
        c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      garage_fullness TEXT,
                      time TEXT
                      )''')
    conn.commit()
    print("Database setup complete")
    return conn


#insert data function
def insert_garage_data(conn, garage_data, time):
    c = conn.cursor()

    for garage_names, details in garage_data.items():
        table_name = garage_names.replace(" ", "_")
        c.execute(f"INSERT INTO {table_name} (garage_fullness, time) VALUES (?, ?)", (details[0], time))

    conn.commit()
    print("Data inserted")
    

#delete data after two minutes for now function
def delete_garage_data(conn, garage_data):
    c = conn.cursor()
    time_threshold = (datetime.now() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')

    for garage_names in garage_data.keys():
        table_name = garage_names.replace(" ", "_")
        c.execute(f"DELETE FROM {table_name} WHERE time < ?", (time_threshold))

    conn.commit()
    print("Old data deleted")



