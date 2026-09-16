import pandas as pd
from datetime import date

df = pd.read_excel("충전소 요금(회원가).xlsx")

env_df = df[df["사업자 (CPO)"] == "기후에너지환경부"]

print(env_df.head())
print(len(env_df))

price_cols = ["완속(30kW 미만)",
              "중속(30~49kW)",
              "급속(50~99kW)",
              "급속(100~199kW)",
              "초급속(200kW 이상)"]

unique_prices = env_df[price_cols].drop_duplicates()

print(unique_prices)

prices = unique_prices.iloc[0]

data = [
    ["기후에너지환경부","slow", "under_30kw", "member", prices["완속(30kW 미만)"], date.today().isoformat()],
    ["기후에너지환경부","fast", "30_49kw", "member", prices["중속(30~49kW)"], date.today().isoformat()],
    ["기후에너지환경부","fast", "50_99kw", "member", prices["급속(50~99kW)"], date.today().isoformat()], 
    ["기후에너지환경부","fast", "100_199kw", "member", prices["급속(100~199kW)"], date.today().isoformat()],
    ["기후에너지환경부","fast", "200_kw", "member", prices["초급속(200kW 이상)"], date.today().isoformat()]
]

env_final = pd.DataFrame(
    data,
    columns=[
        "operator",
        "charger_type",
        "power_band",
        "customer_type",
        "price_per_kwh",
        "crawl_date"
    ]
)

env_final["effective_date"] = "2026-08-01"
env_final["source_url"] = "https://ev.or.kr/nportal/evcarInfo/initEvcarChargePriceV2.do"

non_member_df = env_final.copy()

non_member_df["customer_type"] = "non_member"

env_final = pd.concat(
    [env_final, non_member_df], ignore_index=True
)

print(env_final)

#csv 저장
env_final.to_csv(
    "data/Ministry_environment.csv",
    index = False,
    encoding="utf-8-sig"
)
print("\n기후에너지환경부 요금 데이터 저장 완료")

