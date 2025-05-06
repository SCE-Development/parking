import logging
import os

# Set up logging before anything else
logging.basicConfig(
    format="%(asctime)s.%(msecs)03dZ %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,  # Set default level to INFO
    force=True,  # Ensure our configuration is applied
)

# Rest of the imports
import asyncio #used for async await 
import urllib3 #more advanced HTTP request handling (GET, POST, ...)
from bs4 import BeautifulSoup #parsing HTML/web scraping
from datetime import datetime
import uvicorn #server that works with FastAPI and is useful for running python backend
from fastapi import FastAPI #quickly set up python backend
import sqlhelper
import time
import pytz
import threading #used to run something periodically?
from typing import Optional
from contextlib import asynccontextmanager #used with threading

from fastapi.middleware.cors import CORSMiddleware #handling CORS

# Create loggers
logger = logging.getLogger("parking_helper")
main_logger = logging.getLogger("parking_main")

# Set logging level based on environment variable
verbose_level = int(os.getenv("VERBOSE", "0"))
logging.getLogger().setLevel(logging.ERROR - (verbose_level * 10))

last_update_timestamp = None
last_garage_data = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    main_logger.info("Starting up parking server...")
    should_run.set()
    global helper_thread
    if helper_thread is None or not helper_thread.is_alive():
        helper_thread = threading.Thread(target=helper_thread_func, daemon=True)
        helper_thread.start()
        main_logger.info("Helper thread initialized")
    yield
    # Shutdown
    main_logger.info("Shutting down parking server...")
    should_run.clear()
    if helper_thread and helper_thread.is_alive():
        helper_thread.join(timeout=1)
        main_logger.info("Helper thread stopped")

app = FastAPI(lifespan=lifespan)

origins = [
    "http://frontend:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(cert_reqs="CERT_NONE", assert_hostname=False)

garage_addresses = []
GARAGE_NAMES = ["North_Garage", "South_Garage", "West_Garage", "South_Campus_Garage"]

# Global variable to store the helper thread
helper_thread: Optional[threading.Thread] = None
should_run = threading.Event()

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# fastapi endpoints
#yuwen: main scraping function using BeautifulSoup4
@app.get("/parking")
async def insert_garage_data():
    global last_update_timestamp, last_garage_data

    response = http.request("GET", "https://sjsuparkingstatus.sjsu.edu")
    data = response.data.decode("utf-8")
    soup = BeautifulSoup(data, "html.parser")

    timestamp_tag = soup.find('p', class_='timestamp')
    if not timestamp_tag:
        logger.warning("Timestamp not found on the page")
        return None

    current_timestamp = timestamp_tag.text.strip().split("Last updated ")[-1].split(" Refresh")[0]

    if current_timestamp == last_update_timestamp and last_garage_data is not None:
        logger.info("Timestamp hasn't changed, skipping database update")
        return last_garage_data

    garage_div = soup.find(
        "div", class_="garage"
    )
    garage_names = garage_div.find_all("h2", class_="garage__name")
    garage_fullness = garage_div.find_all("span", class_="garage__fullness")

    garage_data = {}
    for name, fullness in zip(garage_names, garage_fullness):
        # Extract percentage number from string like "75% Full"
        percentage = int(fullness.text.strip().split("%")[0])
        garage_data[name.text.strip().replace(" ", "_")] = percentage

    # Update the timestamp and last known data
    last_update_timestamp = current_timestamp
    last_garage_data = garage_data

    timestamp = get_time()
    for garage in GARAGE_NAMES:
        sqlhelper.insert_garage_data(None, garage, f"{garage_data[garage]}% Full", timestamp)
        logger.info(f"Inserted data for {garage} at {timestamp}, last update timestamp: {last_update_timestamp}")

    # return {"test": "hi"}
    return garage_data

@app.get("/parking-history")
async def get_garage_history(garage_name):
    print(f"endpoint hit garage_name: {garage_name}")
    # todo: input validation: garage_name should be a string, and has to be one of the 4 garage names
    data = sqlhelper.get_garage_data(None, garage_name)
    # print(f"data: {data}")
    return data

# @app.get("/test")
# async def test():
#     return {"hi changed": "bye"}

@app.get("/")
async def root():
    return "Welcome to SJSU Parking!"

def helper_thread_func():
    logger.info("Helper thread started.")
    while should_run.is_set():
        current_time = datetime.now(pytz.timezone("US/Pacific"))
        logger.info(f"Current time: {current_time}")
        if current_time.hour >= 7 and current_time.hour < 21:
            try:
                # Between 7am-9pm, call endpoint
                asyncio.run(insert_garage_data())
            except Exception as e:
                logger.error(
                    f"An error occurred: {e}", exc_info=True
                )
        else:
            logger.info("Outside operating hours (7 AM - 9 PM PST). Sleeping...")
            # Sleep for an hour before checking again
            time.sleep(3600)
            continue

        # Calling endpoint every minute
        time.sleep(60)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
