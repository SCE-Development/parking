import asyncio
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
import uvicorn
from fastapi import FastAPI
import sqlhelper
import random
import logging
import time
from args import get_args
import pytz
import threading

app = FastAPI()
args = get_args()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

DB_FILE = args.dbfile
garage_addresses = []
GARAGE_NAMES = ["North_Garage", "South_Garage", "West_Garage", "South_Campus_Garage"]
sqlhelper.maybe_create_table(DB_FILE, GARAGE_NAMES)

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#fastapi endpoints
@app.get("/parking")
async def get_garage_data():
    response = http.request('GET', 'https://sjsuparkingstatus.sjsu.edu')
    data = response.data.decode('utf-8')
    soup = BeautifulSoup(data, 'html.parser')
    garage_div = soup.find('div', class_='garage')  # ensures we are only looking in the scope of the garage div
    garage_names = garage_div.find_all('h2', class_='garage__name')
    garage_fullness = garage_div.find_all('span', class_='garage__fullness')
    garage_addresses = garage_div.find_all('a')
    href_links = [link.get('href') for link in garage_addresses]

    garage_data = {}  # Reset garage data for each request
    for name, fullness, address in zip(garage_names, garage_fullness, href_links):
        garage_data[name.text.strip().replace(" ", "_")] = [fullness.text.strip(), address]
        garage_addresses = [info[1] for info in garage_data.values()]    

    
    timestamp = get_time()
    for garage in GARAGE_NAMES:
        sqlhelper.insert_garage_data(DB_FILE, garage, garage_data[garage][0], timestamp)
        sqlhelper.delete_garage_data(DB_FILE, garage)

    return garage_data

logging.Formatter.converter = time.gmtime
logging.basicConfig(
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level= logging.ERROR - (args.verbose*10),
)

@app.get("/")
async def root():
    return "Welcome to SJSU Parking!"

def helper_thread():
    print("Helper thread started.")  
    while True:
        current_time = datetime.now(pytz.timezone('US/Pacific'))
        print(f"Current time: {current_time}")
        if current_time.hour >= 8 and current_time.hour < 18:
            try:
                # Between 8am-6pm, call endpoint
                asyncio.run(get_garage_data())  # Run the coroutine in the event loop
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Stopping data retrieval as it's past 6:00 PM PST.")
            break

        # Calling endpoint every minute
        time.sleep(20) 

if __name__ == 'server':
    helper = threading.Thread(target=helper_thread, daemon=True)
    helper.start()

if __name__ == "__main__":
    args = get_args()
    uvicorn.run("server:app", host=args.host, port=args.port, reload=True, )
