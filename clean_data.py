import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

ITEM_KEYWORDS = [
    "Ayam",
    "Beras",
    "Telur",
    "Minyak Masak",
    "Gula",
]


def load_raw():
    prices = pd.read_parquet(RAW_DIR / "pricecatcher_combined_raw.parquet")
    items = pd.read_parquet(RAW_DIR / "lookup_item.parquet")
    premises = pd.read_parquet(RAW_DIR / "lookup_premise.parquet")
    return prices, items, premises


def clean(prices: pd.DataFrame, items: pd.DataFrame, premises: pd.DataFrame) -> pd.DataFrame:
    print(f"Raw rows: {len(prices):,}")

    prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
    prices["price"] = pd.to_numeric(prices["price"], errors="coerce")

    before = len(prices)
    prices = prices.dropna(subset=["date", "price", "item_code", "premise_code"])
    print(f"Dropped {before - len(prices):,} rows with missing date/price/codes")

    before = len(prices)
    prices = prices[prices["price"] > 0]
    print(f"Dropped {before - len(prices):,} rows with price <= 0")

    before = len(prices)
    prices = prices.drop_duplicates(subset=["date", "premise_code", "item_code", "price"])
    print(f"Dropped {before - len(prices):,} exact duplicate rows")

    prices = prices.merge(items, on="item_code", how="left")
    prices = prices.merge(premises, on="premise_code", how="left")

    missing_item_name = prices["item"].isna().sum()
    if missing_item_name:
        print(f"Warning: {missing_item_name:,} rows had no matching item lookup (dropping)")
        prices = prices.dropna(subset=["item"])

    pattern = "|".join(ITEM_KEYWORDS)
    mask = prices["item"].str.contains(pattern, case=False, na=False)
    filtered = prices[mask].copy()
    print(f"\nFiltered to keywords {ITEM_KEYWORDS}: {len(filtered):,} rows "
          f"({filtered['item'].nunique()} distinct item variants)")

    def remove_outliers(group):
        q1, q3 = group["price"].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        return group[(group["price"] >= lower) & (group["price"] <= upper)]

    before = len(filtered)
    filtered = filtered.groupby("item_code", group_keys=False).apply(remove_outliers)
    print(f"Removed {before - len(filtered):,} outlier rows (IQR method, per item)")

    return filtered


def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    daily = (
        df.groupby(["date", "item", "state"], as_index=False)["price"]
        .mean()
        .rename(columns={"price": "avg_price"})
    )
    return daily.sort_values(["item", "state", "date"])


def main():
    prices, items, premises = load_raw()
    cleaned = clean(prices, items, premises)

    cleaned.to_csv(CLEAN_DIR / "pricecatcher_cleaned_full.csv", index=False)
    print(f"\nSaved full cleaned (row-level) data: {len(cleaned):,} rows -> "
          f"data/clean/pricecatcher_cleaned_full.csv")

    daily = aggregate_daily(cleaned)
    daily.to_csv(CLEAN_DIR / "daily_avg_price_by_item_state.csv", index=False)
    print(f"Saved daily aggregated data: {len(daily):,} rows -> "
          f"data/clean/daily_avg_price_by_item_state.csv")

    print("\nPreview:")
    print(daily.head(10).to_string(index=False))


if __name__ == "__main__":
    main()