import requests
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from bs4 import BeautifulSoup
from datetime import date

url = "https://www.happecharger.com/happecharger/membership"

response = requests.get(url)

# 바로 Beautifulsoup 가능

soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table")
print("table 개수", len(tables))

for i, table in enumerate(tables):
    print("\n ----- TABLE -----")
    print(table.get_text(" ",strip=True))

table = tables[0]
rows = table.find_all("tr")

print("tr 개수", len(rows))

for i, row in enumerate(rows):
    cells = row.find_all(["th", "td"])

    print("\nrow", i)

    for j, cell in enumerate(cells):
        print(
            j,
            cell.get_text(" ", strip=True),
            "rowspan=", cell.get("rowspan"),
            "colspan=", cell.get("colspan")
        )

fee_data = []

#급속
cells1 = rows[1].find_all(["th", "td"])
fast_raw = cells1[1].get_text(" ", strip=True)
fast_member = float(cells1[2].get_text(" ", strip=True))
non_member_price = float(cells1[3].get_text(" ", strip=True))

#완속
cells2 = rows[2].find_all(["th", "td"])
slow_raw = cells2[0].get_text(" ", strip=True)
slow_member = float(cells2[1].get_text(" ", strip=True))

charger_data = [
    (fast_raw, "fast", fast_member),
    (slow_raw, "slow", slow_member)
]

for raw_type, charger_type, member_price in charger_data:
    fee_data.append({
        "operator": "Happecharger",
        "charger_raw_type": raw_type,
        "charger_type": charger_type,
        "customer_type": "member",
        "price_per_kwh": member_price,
        "effective_date": "2025-08-01",
        "crawl_date": date.today().isoformat(),
        "source_url": url
    })

    fee_data.append({
        "operator": "Happecharger",
                "charger_raw_type": raw_type,
                "charger_type": charger_type,
                "customer_type": "non_member",
                "price_per_kwh": non_member_price,
                "effective_date": "2025-08-01",
                "crawl_date": date.today().isoformat(),
                "source_url": url
    })


df = pd.DataFrame(fee_data)


#csv 저장
df.to_csv(
    "data/happecharger_fee.csv",
    index = False,
    encoding="utf-8-sig")
