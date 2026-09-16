import requests
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from bs4 import BeautifulSoup
from datetime import date

url = "https://www.e-pit.co.kr/brand-web/epit/charging-fare"
response = requests.get(url)

print("status code:", response.status_code)
print("325 존재:", "325" in response.text)
print("프라임 존재:", "프라임" in response.text)

# selenium 
options = Options()
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(3)
rendered_html = driver.page_source
print("325 존재:", "325" in rendered_html)
print("프라임 존재:", "프라임" in rendered_html)

soup = BeautifulSoup(
    rendered_html,
    "html.parser"
)

print(soup.get_text(" ", strip=True)[:3000])


rows = soup.find_all("tr")

for row in rows:
    text = row.get_text(" ", strip=True)

    if "325" in text and "460" in text and "530" in text:
        cells = row.find_all("td")

        for cell in cells:
            print(cell.get_text(" ", strip=True))

prices = []

for cell in cells:
    text = cell.get_text(strip=True)
    number = re.search(r"\d+", text)

    if number:
        prices.append(int(number.group()))

print(prices)

fee_data = [
    {
        "operator": "E-pit",
        "charger_type": "초급속",
        "customer_type": "prime_member",
        "price_per_kwh": prices[0],
        "effective_date": None,
        "crawl_date": date.today(),
        "source_url": url
    },
    {
        "operator": "E-pit",
        "charger_type": "초급속",
        "customer_type": "member",
        "price_per_kwh": prices[1],
        "effective_date": None,
        "crawl_date": date.today(),
        "source_url": url
    },
    {
        "operator": "E-pit",
        "charger_type": "초급속",
        "customer_type": "non_member",
        "price_per_kwh": prices[2],
        "effective_date": None,
        "crawl_date": date.today(),
        "source_url": url
    }
]

df = pd.DataFrame(fee_data)
print(repr(df))

#csv 저장
df.to_csv(
    "data/raw/epit_fee.csv",
    index = False,
    encoding="utf-8-sig"
)

driver.quit()