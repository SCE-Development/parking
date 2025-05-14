import psycopg2 #postgreSQL
import csv #for importing data from csv or txt files

def get_db_connection():
    return psycopg2.connect(
        dbname="test_db",
        user="root",
        password="root",
        host="db",  # This is the service name in docker-compose
        port="5432",
    )

"""
- **how to insert into database?
"""

def insert_csv_data(filePath: str):
    # conn = get_db_connection()
    # cur = conn.cursor()

    # r means open in read mode
    with open(filePath, 'r') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
        # for row in reader:
            if i == 15:
                break
            garage = row[1].replace(" ", "_")
            fullness = "{} Full".format(row[2].replace(" ", ""))
            timestamp = row[3].replace(" ", "T")[0:19]
            print(garage + ", " + fullness + ", " + timestamp)

            # query = """
            # INSERT INTO parking_data (garage_name, garage_fullness, timestamp) 
            # VALUES (%s, %s, %s)
            # """
            # cur.execute(query, (garage, fullness, timestamp))
            # conn.commit()

if __name__ == "__main__":
    insert_csv_data('C:/ASUS_Users/SCE/parking/backend/sce_parking_garage_info')