import requests
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from bs4 import BeautifulSoup
from datetime import date

url = "https://m.skelectlink.co.kr/service/membership"
response = requests.get(url)

print("status code:", response.status_code)
print("315 존재:", "315" in response.text)
print("스타터 존재:", "스타터" in response.text)



with open("sk_electlink.html", "w", encoding = "utf-8") as f:
    f. write(response.text)
print("sk_electlink HTML 저장 완료")

soup = BeautifulSoup(response.text, "html.parser")

rows = soup.select("tr")
print("tr 개수:", len(rows))

for row in rows:
    text = row.get_text(
        "", strip=True
    )
    if any (plan in text for plan in ["스타터", "베이직", "프로", "마스터"]):
        print(text)


for row in rows:
    cells = row.select("th, td")
    values = [cell.get_text("", strip=True) for cell in cells]

    if values:
        print(values)

plan_names = ["스타터", "베이직", "프로", "마스터"]
subscription_data = []

for row in rows:
    cells = row.select("th, td")
    values = [cell.get_text("", strip = True) for cell in cells]

    if len(values) < 5:
        continue

    if values[0] not in plan_names:
        continue

    plan_name = values[0]
    price_per_kwh = float(
        values[1].replace("원", "").replace(",","")
    )

    quota_text = values[2]

    monthly_fee = int(
        values[4].replace("원","").replace(",","")
    )

    if "무제한" in quota_text:
        quota_kwh = None
    else:
        quota_kwh = float(
            quota_text.lower().replace("kwh","").replace(",","").strip()
        )


    subscription_data.append({
        "operator": "SK일렉링크",
        "plan_name": plan_name,
        "charger_type": "급속",
        "customer_type": "subscription",
        "price_per_kwh": price_per_kwh,
        "quota_kwh": quota_kwh,
        "monthly_fee_kwh": monthly_fee,
        "crawl_date": date.today().isoformat(),
        "source_url": url
    })

subscription_df = pd.DataFrame(subscription_data)
print("\n=== SK일렉링크 구독요금 ===")
print((subscription_df).to_string(index=False))

print("\n=== 수집 행 개수 ===")
print(len(subscription_df))





page_text = soup.get_text(" ", strip=True)

match = re.search(
    r"(\d+)\s*원\s*→\s*315", page_text
)

if match:
    regular_fast_price = float(
        match.group(1)
    )
else:
    regular_fast_price = None

print("일반 급속 충전 요금:", regular_fast_price)

regular_data = [{
    "operator": "SK일렉링크",
    "charger_type": "급속",
    "customer_type": "member",
    "price_per_kwh": regular_fast_price,
    "crawl_date": date.today().isoformat(),
    "source_url": url
}]

regular_df = pd.DataFrame(
    regular_data
)

print("\n=== SK일렉링크 일반회원 요금 ===")
print(regular_df)


regular_url = "https://m.skelectlink.co.kr/charging-plans?modal=charging-price"

regular_response = requests.get(regular_url)

print("\n=== 일반 충전요금 페이지 조사 ===")
print("status code:", regular_response.status_code)

print("391 존재:", "391" in regular_response.text)
print("295 존재:", "295" in regular_response.text)
print("590 존재:", "590" in regular_response.text)
print("445 존재:", "445" in regular_response.text)
print("한전 아파트 충전소 존재:", "한전 아파트 충전소" in regular_response.text)

with open("sk_electlink_regular.html", "w", encoding = "utf-8") as f:
    f.write(regular_response.text)

print("SK일렉링크 일반요금 HTML 저장 완료")

# selenium 

general_url = "https://m.skelectlink.co.kr/charging-plans?modal=charging-price"
options = Options()
driver = webdriver.Chrome(options=options)
driver.get(general_url)
time.sleep(3)

rendered_html = driver.page_source

print("SK일렉링크 회원 존재:",
      "SK일렉링크 회원" in rendered_html)

print("비회원 존재:",
      "비회원" in rendered_html)

with open(
    "sk_electlink_general_rendered.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(rendered_html)

driver.quit()

general_soup = BeautifulSoup(
    rendered_html,
    "html.parser"
)

general_rows = general_soup.select("tr")
print("\n=== SK 일반요금표 행 확인 ===")

for row in general_rows:
    text = row.get_text(" ", strip=True)
    if text:
        print(repr(text))

    

general_data = []

fast_text = None
slow_text = None
non_member_text = None

for row in general_rows:
    text = row.get_text("\n", strip=True)
    lines = text.splitlines()

    if len(lines) >= 2 and lines[0] == "SK일렉링크":
        if lines[1] == "급속":
            fast_text = " ".join(lines[1:])

        elif lines[1] == "완속":
            slow_text = " ".join(lines[1:])

    elif len(lines) >= 1 and lines[0] == "비회원":
        non_member_text = " ".join(lines)

print("급속:", fast_text)
print("완속:", slow_text)
print("비회원:", non_member_text)




fast_under_30 = float(
    re.search(
        r"30kW 이하\s*([0-9.]+)",
        fast_text
    ).group(1)
)

fast_over_30 = float(
    re.search(
        r"30kW 초과\s*([0-9.]+)",
        fast_text
    ).group(1)
)

slow_public = float(
    re.search(
        r"공용 충전소\s*([0-9.]+)",
        slow_text
    ).group(1)
)

slow_apartment = float(
    re.search(
        r"아파트 충전소\s*([0-9.]+)",
        slow_text
    ).group(1)
)

non_member_price = float(
    re.search(
        r"비회원\s*([0-9.]+)",
        non_member_text
    ).group(1)
)



general_data = [
    {
        "operator": "SK일렉링크",
        "plan_name": None,
        "charger_type": "급속",
        "power_band": "30kW 이하",
        "customer_type": "member",
        "price_per_kwh": fast_under_30,
        "monthly_fee_krw": None,
        "quota_kwh": None,
        "crawl_date": date.today().isoformat(),
        "source_url": general_url
    },
    {
        "operator": "SK일렉링크",
        "plan_name": None,
        "charger_type": "급속",
        "power_band": "30kW 초과",
        "customer_type": "member",
        "price_per_kwh": fast_over_30,
        "monthly_fee_krw": None,
        "quota_kwh": None,
        "crawl_date": date.today().isoformat(),
        "source_url": general_url
    },
    {
        "operator": "SK일렉링크",
        "plan_name": None,
        "charger_type": "완속",
        "power_band": "공용 충전소",
        "customer_type": "member",
        "price_per_kwh": slow_public,
        "monthly_fee_krw": None,
        "quota_kwh": None,
        "crawl_date": date.today().isoformat(),
        "source_url": general_url
    },
    {
        "operator": "SK일렉링크",
        "plan_name": None,
        "charger_type": "완속",
        "power_band": "아파트 충전소",
        "customer_type": "member",
        "price_per_kwh": slow_apartment,
        "monthly_fee_krw": None,
        "quota_kwh": None,
        "crawl_date": date.today().isoformat(),
        "source_url": general_url
    },
    {
        "operator": "SK일렉링크",
        "plan_name": None,
        "charger_type": "전체",
        "power_band": None,
        "customer_type": "non_member",
        "price_per_kwh": non_member_price,
        "monthly_fee_krw": None,
        "quota_kwh": None,
        "crawl_date": date.today().isoformat(),
        "source_url": general_url
    }
]

general_df = pd.DataFrame(general_data)

print("\n=== SK일렉링크 자체 일반요금 ===")
print(general_df.to_string(index=False))
print("일반요금 수집 행 개수:", len(general_df))




# 합치기 (subscription4+일반5)
subscription_df["power_band"] = None

sk_fee_df = pd.concat(
    [general_df, subscription_df],
    ignore_index=True
)

column_order = [
    "operator",
    "plan_name",
    "charger_type",
    "power_band",
    "customer_type",
    "price_per_kwh",
    "monthly_fee_krw",
    "quota_kwh",
    "crawl_date",
    "source_url"
]

sk_fee_df = sk_fee_df[column_order]


print("\n=== SK일렉링크 최종 요금 데이터 ===")
print(sk_fee_df.to_string(index=False))

print("\n최종 행 개수:", len(sk_fee_df))

#csv 저장
sk_fee_df.to_csv(
    "data/sk_electlink_fee.csv",
    index = False,
    encoding="utf-8-sig"
)
print("\nSK일렉링크 요금 데이터 저장 완료")