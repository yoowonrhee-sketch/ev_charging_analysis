import requests
import pandas as pd
from datetime import date

url = "https://www.evsis.co.kr/h/chrgr/fee"

response = requests.get(url)

print(response.status_code)
print(response.text[:1000])

from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")
print(soup.prettify()[:3000])

with open("evis.html", "w", encoding = "utf-8") as f:
    f. write(response.text)
print("HTML 저장 완료")


fee_section = soup.select_one("div.content-block-fee")
items = fee_section.select("div.item")
print(f"찾은 요금 블록 수 : {len(items)}")

for item in items:
    print(item.text)
    print("=" * 50)

for item in items:
    uls = item.select("ul")
    print(f"ul 개수 : {len(uls)}")

    for ul in uls:
        print(ul.text)

    print("=" * 50)

fee_data = []
for item in items:

    member_price = None
    subscription_price = None
    non_member_price = None

    uls = item.select("ul")
    for ul in uls:

        text = ul.text
        if "EVIS회원" in text:
            member_price = ul.select_one("span").text

        elif "구독권" in text:
            subscription_price = ul.select_one("span").text

        elif "비회원" in text:
            non_member_price = ul.select_one("span").text

    charger_type = item.select_one(
        "div.h-txt"
    ).text.strip()

    fee_data.append(
        {
            "operator": "EVSIS",
            "charger_type": charger_type,
            "member_price": member_price,
            "subscription_price": subscription_price,
            "non_member_price": non_member_price
        }
    )



df = pd.DataFrame(fee_data)
print(df)

price_columns = [
    "member_price",
    "subscription_price",
    "non_member_price"
]
for column in price_columns:
    df[column] = pd.to_numeric(df[column])

print("\n=== 데이터 타입 ===")
print(df.dtypes)

df["effective_date"] = "2026-05-01"
df["crawl_date"] = date.today().isoformat()
df["source_url"] = url

print("\n=== 최종 EVSIS 요금 데이터 ===")
print(df)

df_long = df.melt(
    id_vars = [
        "operator",
        "charger_type",
        "effective_date",
        "crawl_date",
        "source_url"
    ],
    value_vars = [
        "member_price",
        "subscription_price",
        "non_member_price"
    ],
    var_name = "customer_type",
    value_name = "price_per_kwh"
)

print("\n=== 분석용 long format ===")
print(df_long)

df_long["customer_type"] = df_long["customer_type"].replace(
    {
        "member_price": "member",
        "subscription_price": "subscription",
        "non_member_price": "non_member"
    }
)

df.to_csv(
    "data/evsis_fee_raw.csv",
    index=False,
    encoding="utf-8-sig"
)

df_long.to_csv(
    "data/evsis_fee.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nEVSIS 요금 데이터 저장 완료")

df_raw = pd.read_csv("data/evsis_fee_raw.csv")

print(
    df_raw[
        [
            "member_price",
            "subscription_price",
            "non_member_price"
        ]
    ].to_string()
)