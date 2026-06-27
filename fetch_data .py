import os
import certifi
import pandas as pd
from pathlib import Path

os.environ["SSL_CERT_FILE"] = certifi.where()

MONTHS = ["2026-03", "2026-04", "2026-05"]
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://storage.data.gov.my/pricecatcher"


def download_parquet(url: str, save_path: Path) -> pd.DataFrame:
    print(f"Downloading {url} ...")
    df = pd.read_parquet(url)
    df.to_parquet(save_path)
    print(f"  -> saved to {save_path}  ({len(df):,} rows)")
    return df


def main():
    item_df = download_parquet(f"{BASE_URL}/lookup_item.parquet", RAW_DIR / "lookup_item.parquet")
    premise_df = download_parquet(f"{BASE_URL}/lookup_premise.parquet", RAW_DIR / "lookup_premise.parquet")

    price_frames = []
    for month in MONTHS:
        url = f"{BASE_URL}/pricecatcher_{month}.parquet"
        save_path = RAW_DIR / f"pricecatcher_{month}.parquet"
        df = download_parquet(url, save_path)
        price_frames.append(df)

    prices_df = pd.concat(price_frames, ignore_index=True)
    prices_df.to_parquet(RAW_DIR / "pricecatcher_combined_raw.parquet")
    print(f"\nCombined raw price data: {len(prices_df):,} rows across {len(MONTHS)} months")

    print("\nSample item names available (first 30):")
    print(item_df[["item_code", "item"]].head(30).to_string(index=False))

    print("\nDone. Raw files saved in data/raw/")


if __name__ == "__main__":
    main()