from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import date

url = "https://www.gschargev.co.kr/mobile/mobileCost.html"

with open(
    "chargev_fee.html",
    "r",
    encoding="utf-8"
) as f:
    html = f.read()

print("345 존재:", "345" in html)
print("급속 존재:", "급속" in html)

soup = BeautifulSoup(html, "html.parser")

rows = soup.select("tr")
print("tr 개수:", len(rows))

for row in rows:
    text = row.get_text(
        " ", strip=True
    )
    if "325" in text or "345" in text or "470" in text:
        print(text)


tables = soup.find_all("table")

print("table 개수:", len(tables))

for i, table in enumerate(tables):
    print("\n----- TABLE", i, "-----")
    print(table.get_text(" ", strip=True))

target_table = tables[0]
rows = target_table.find_all("tr")

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
for row in rows[1:]:
    cells = row.find_all(["th","td"])

    raw_type = cells[0].get_text(" ", strip=True)
    member_price = float(cells[1].get_text(strip=True))

    # 출력 기준으로 표준화
    if "3kW" in raw_type or "30kw 미만" in raw_type:
        charger_type = "slow"

    else: charger_type = "fast"


    fee_data.append({
        "operator": "Chargev",
        "charger_raw_type": raw_type,
        "charger_type": charger_type,
        "customer_type": "member",
        "price_per_kwh": member_price,
        "effective_date": "2026-08-01",
        "crawl_date": date.today().isoformat(),
        "source_url": url
    })

    fee_data.append({
            "operator": "Chargev",
            "charger_raw_type": raw_type,
            "charger_type": charger_type,
            "customer_type": "non_member",
            "price_per_kwh": 470,
            "effective_date": "2026-08-01",
            "crawl_date": date.today().isoformat(),
            "source_url": url
        })

df = pd.DataFrame(fee_data)

#csv 저장
df.to_csv(
    "data/chargev_fee.csv",
    index = False,
    encoding="utf-8-sig")

