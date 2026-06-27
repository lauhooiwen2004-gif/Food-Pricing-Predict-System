import pandas as pd
import numpy as np


def load_price_data(filename="daily_avg_price_by_item_state.csv"):
    try:
        df = pd.read_csv(filename)
        df['date'] = pd.to_datetime(df['date'])
        df['days'] = (df['date'] - df['date'].min()).dt.days
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


def get_unique_states(df):
    return sorted(list(df['state'].unique()))


def get_unique_items(df):
    return sorted(list(df['item'].unique()))


def predict_future_price(df, item_name, state_name, target_month):

    filtered_df = df[(df['item'] == item_name) & (df['state'] == state_name)]

    if filtered_df.empty:
        return None

    X = filtered_df['days'].values
    Y = filtered_df['avg_price'].values
    n = len(X)
    historical_avg = float(np.mean(Y))

    if n < 2:
        return round(historical_avg, 2), historical_avg, 0.0, "Stable", []

    sum_x = float(np.sum(X))
    sum_y = float(np.sum(Y))
    sum_xy = float(np.sum(X * Y))
    sum_x2 = float(np.sum(X ** 2))

    denominator = (n * sum_x2) - (sum_x ** 2)
    m = ((n * sum_xy) - (sum_x * sum_y)) / denominator if denominator != 0 else 0.0
    c = (sum_y - (m * sum_x)) / n

    target_day = (target_month - 3) * 30.5 + 15
    base_predicted_price = (m * target_day) + c


    event_modifiers = 1.0
    reasons = []

    # Convert to lower case
    item_lower = item_name.lower()

    # Monsoon Season
    if target_month in [11, 12, 1] and (
            "bayam" in item_lower or "sardin" in item_lower or "kembung" in item_lower or "ayam" in item_lower):
        event_modifiers += 0.20
        reasons.append(
            "🌧️ **Monsoon Season Effect:** Severe year-end rainfall and potential floods in agricultural zones/coastal regions have triggered supply chain disruptions and lower harvest yields.")

    # When during festival
    if target_month == 2 and ("ayam" in item_lower or "telur" in item_lower):
        event_modifiers += 0.12
        reasons.append(
            "🧧 **Chinese New Year Festival:** High domestic consumer demand for poultry and eggs during the holiday season driving local market premium rates upwards.")
    elif target_month == 5 and (
            "ayam" in item_lower or "dada" in item_lower or "paha" in item_lower or "whole leg" in item_lower):
        event_modifiers += 0.15
        reasons.append(
            "🌙 **Hari Raya Aidilfitri Festival:** Massive nationwide surge in poultry and meat consumption for traditional festive cooking, leading to structural demand-pull inflation.")

    # When Price Control Policy Happened
    if "sst5%" in item_lower or "local rice" in item_lower or "paket" in item_lower:
        event_modifiers = 1.0
        base_predicted_price = historical_avg
        reasons.append(
            "🏛️ **Government Subsidized / Price Control Item:** Price remains strictly anchored and stable due to statutory price ceilings and direct market interventions by KPDN.")


    final_predicted_price = base_predicted_price * event_modifiers


    if final_predicted_price < historical_avg * 0.5:
        final_predicted_price = historical_avg * 0.8
    elif final_predicted_price > historical_avg * 2.0:
        final_predicted_price = historical_avg * 1.6

    # Trend
    if m > 0.001:
        trend = "Increasing Trend "
    elif m < -0.001:
        trend = "Decreasing Trend "
    else:
        trend = "Stable Trend "


    if not reasons:
        if m > 0:
            reasons.append(
                "📈 **Historical Market Momentum:** Price is experiencing a gradual organic increase based on sequential growth patterns captured between March and May.")
        else:
            reasons.append(
                "📉 **Improved Market Supply:** Price is experiencing a steady structural decline due to consistent production cycles and stable logistic distributions recorded previously.")

    return round(final_predicted_price, 2), round(historical_avg, 2), round(m, 5), trend, reasons