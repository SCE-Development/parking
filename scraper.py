import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def scrape_parking_data_and_insert_into_db():
    # Suppress the warning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Define the URL to scrape
    url = 'https://sjsuparkingstatus.sjsu.edu'

    # Send a GET request to the URL with SSL verification turned off
    response = requests.get(url, verify=False)

    # Check if the request was successful
    if response.status_code == 200:
        # Decode the response content and create a BeautifulSoup object
        data = response.content.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')

        # Example of scraping logic
        garage_div = soup.find('div', class_='garage')  # Adjust this based on actual HTML structure
        garage_names = garage_div.find_all('h2', class_='garage__name')
        garage_fullness = garage_div.find_all('span', class_='garage__fullness')

        # Process the scraped data
        garage_data = []
        for name, fullness in zip(garage_names, garage_fullness):
            garage_data.append((name.text.strip(), fullness.text.strip()))
        
        print(garage_data)
        try:
            print("Inserting to the PostgreSQL database...")
            conn = psycopg2.connect(
                dbname=os.getenv('dbname'),        
                user=os.getenv('user'),             
                password=os.getenv('password'),         
                host=os.getenv('host'),        
                port=os.getenv('port')              
            )
            cursor = conn.cursor()

            # Insert data into the table
            insert_query = '''
            INSERT INTO garage_info (garage_name, fullness_percentage, timestamp)
            VALUES (%s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Los_Angeles')
            '''
            cursor.executemany(insert_query, garage_data)
            conn.commit()

            print(f"Inserted {len(garage_data)} records into the garage_info table.")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Close the cursor and connection
            cursor.close()
            conn.close()
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def display_parking_data_from_db():
    try:
            print("Selecting from to the PostgreSQL database...")
            conn = psycopg2.connect(
                dbname=os.getenv('dbname'),        
                user=os.getenv('user'),             
                password=os.getenv('password'),         
                host=os.getenv('host'),        
                port=os.getenv('port')              
            )
            cursor = conn.cursor()

            # Insert data into the table
            select_query = '''
            SELECT * FROM garage_info
            '''
            cursor.execute(select_query)
            results = cursor.fetchall()
            for row in results:
                print(row)
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

if __name__ == '__main__':
    scrape_parking_data_and_insert_into_db()
    display_parking_data_from_db()


