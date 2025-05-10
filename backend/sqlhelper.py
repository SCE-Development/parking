import psycopg2 #postgreSQL
from datetime import datetime, timedelta #used for deleting data
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging #debugging messages

logger = logging.getLogger("parking_db")


def get_db_connection():
    return psycopg2.connect(
        dbname="test_db",
        user="postgres",
        password="root",
        host="db",  # This is the service name in docker-compose
        port="5432",
    )

def insert_garage_data(dbfile: str, garage, fullness, timestamp):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        query = """
            INSERT INTO parking_data (garage_name, garage_fullness, timestamp) 
            VALUES (%s, %s, %s)
        """
        cur.execute(query, (garage, fullness, timestamp))
        conn.commit()
        logger.info(f"Data inserted into {garage} at {timestamp}")

        # Verify the insertion
        cur.execute(
            """
            SELECT * FROM parking_data 
            WHERE garage_name = %s 
            ORDER BY timestamp DESC 
            LIMIT 1
        """,
            (garage,),
        )
        logger.debug(f"Inserted data: {cur.fetchone()}")

    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def get_garage_data(dbfile: str, garage, time=None):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        if time:
            # print("queried with timestamp: ")
            query = """
                SELECT * FROM parking_data 
                WHERE garage_name = %s AND timestamp >= %s
                ORDER BY timestamp DESC
            """
            cur.execute(query, (garage, time))
        else:
            query = """
                SELECT * FROM parking_data 
                WHERE garage_name = %s 
                ORDER BY timestamp DESC
            """
            cur.execute(query, (garage,))

        return cur.fetchall()
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def delete_garage_data(dbfile: str, garage):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        time_threshold = datetime.now() - timedelta(weeks=2)
        query = """
            DELETE FROM parking_data 
            WHERE garage_name = %s AND timestamp < %s
        """
        cur.execute(query, (garage, time_threshold))
        conn.commit()
        logger.info(f"Old data deleted for {garage}")
    except Exception as e:
        logger.error(f"Error deleting data: {e}")
    finally:
        cur.close()
        conn.close()
