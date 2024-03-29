import urllib3
from bs4 import BeautifulSoup
from fastapi import FastAPI
import uvicorn

app = FastAPI()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)


garage_data = {}

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
        garage_data[name.text.strip()] = [fullness.text.strip(), address]

    print(garage_data)
    return garage_data

get_garage_data()


if __name__ == "__main__":
    uvicorn.run("server:app", port=8000, reload=True)