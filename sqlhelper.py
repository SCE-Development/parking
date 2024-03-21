import sqlite3

#database setup function
def setup_database(dbfile):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS garage_status
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  garage_names TEXT, 
                  garage_fullness TEXT, 
                  garage_addresses TEXT,
                  timestamp TEXT DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    print("Database setup complete")
    return conn

#insert data function
def insert_garage_data(conn,garage_data):
    c = conn.cursor()
    sql = "INSERT INTO garage_status (garage_names, garage_fullness, garage_addresses) VALUES (?, ?, ?)"


    for garage_names, details in garage_data.items():
         c.execute(sql, (garage_names, details[0], details[1]))
    conn.commit()
    print("Data inserted")

    

#delete data after two minutes for now function
def delete_garage_data(conn):
    c = conn.cursor()
    c.execute("DELETE FROM garage_status WHERE timestamp < datetime('now', '-2 minutes')")
    conn.commit()
    
    print("Old data deleted")
