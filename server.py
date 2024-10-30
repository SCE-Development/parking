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
import asyncio
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
import uvicorn
from fastapi import FastAPI
import sqlhelper
import time
import pytz
import threading
from typing import Optional
from contextlib import asynccontextmanager

# Create loggers
logger = logging.getLogger("parking_helper")
main_logger = logging.getLogger("parking_main")

# Set logging level based on environment variable
verbose_level = int(os.getenv("VERBOSE", "0"))
logging.getLogger().setLevel(logging.ERROR - (verbose_level * 10))

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
@app.get("/parking")
async def get_garage_data():
    response = http.request("GET", "https://sjsuparkingstatus.sjsu.edu")
    data = response.data.decode("utf-8")
    soup = BeautifulSoup(data, "html.parser")
    garage_div = soup.find(
        "div", class_="garage"
    )  # ensures we are only looking in the scope of the garage div
    garage_names = garage_div.find_all("h2", class_="garage__name")
    garage_fullness = garage_div.find_all("span", class_="garage__fullness")
    garage_addresses = garage_div.find_all("a")
    href_links = [link.get("href") for link in garage_addresses]

    garage_data = {}  # Reset garage data for each request
    for name, fullness, address in zip(garage_names, garage_fullness, href_links):
        garage_data[name.text.strip().replace(" ", "_")] = [
            fullness.text.strip(),
            address,
        ]

    timestamp = get_time()
    for garage in GARAGE_NAMES:
        sqlhelper.insert_garage_data(None, garage, garage_data[garage][0], timestamp)
        sqlhelper.delete_garage_data(None, garage)
        logger.info(f"Inserted data for {garage} at {timestamp}")

    return garage_data

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
                asyncio.run(get_garage_data())
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
