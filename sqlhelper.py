import sqlite3
from datetime import datetime, timedelta    

#database setup function
def maybe_create_table(dbfile: str, garage_names):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    for garage_name in garage_names:
        c.execute(f'''CREATE TABLE IF NOT EXISTS {garage_name} (
                      id INTEGER PRIMARY KEY,
                      garage_fullness TEXT,
                      time TEXT
                      )''')
    conn.commit()
    print("Database setup complete")
    return conn

#insert data function
def insert_garage_data(dbfile: str, garage, fullness, timestamp):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    # delete_garage_data()
    print(f"{garage}")
    try:
        query = f"INSERT INTO {garage} (garage_fullness, time) VALUES (?, ?)"
        c.execute(query, [fullness, timestamp])
        conn.commit()
    except Exception as e:
        print(e)
        return False

    conn.commit()
    print("Data inserted")
    c.execute(f"SELECT * FROM {garage}")
    print(c.fetchall())

def get_garage_data(dbfile: str, garage, time=None):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    try:
        query = f"SELECT * FROM {garage}"
        c.execute(query)
        return c.fetchall()
    except Exception as e:
        print(e)

#delete data after two weeks
def delete_garage_data(dbfile: str, garage):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    time_threshold = (datetime.now() - timedelta(weeks=2)).strftime('%Y-%m-%d %H:%M:%S')
    print("TIME:",time_threshold)
    try:
        query = f"DELETE FROM {garage} WHERE time < ?"
        c.execute(query, (time_threshold,))
        conn.commit()
        print("Old data deleted")
    except Exception as e:
        print(e)



