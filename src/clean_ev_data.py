import pandas as pd

def clean_data(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna() 

    df["brand"] = df["brand"].str.strip().str.lower()

    brand_mapping = {
        "tesla": "테슬라",
        "kia": "기아",
        "hyundai": "현대"
    }
    df["brand"] = df["brand"].replace(brand_mapping)


    df["range_km"] = (
        df["range_km"]
        .astype(str)
        .str.replace("km", "")
        .astype(int)
    )

    return df


if __name__ == "__main__":

    file_path = "data/ev_models.csv"

    clean_df = clean_data(file_path)

    print("\n=== 전처리 완료 ===")
    print(clean_df)

    clean_file_path = "data/ev_models_clean.csv"
    clean_df.to_csv(clean_file_path, index = False)
    print("정제 데이터 저장 완료")
    



