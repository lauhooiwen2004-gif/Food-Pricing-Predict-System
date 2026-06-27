import streamlit as st
import pandas as pd
from function import load_price_data, get_unique_states, get_unique_items, predict_future_price

st.set_page_config(page_title="Malaysia Food Price Predictor", page_icon="📊", layout="wide")


@st.cache_data
def get_data():
    return load_price_data()


df = get_data()

if df is not None:
    states = get_unique_states(df)
    items = get_unique_items(df)

    # ==========================================
    #              SIDEBAR
    # ==========================================
    st.sidebar.header("⚙️ Prediction Settings")
    selected_state = st.sidebar.selectbox("1. Select State ", states)
    selected_item = st.sidebar.selectbox("2. Select Food Item ", items)

    month_names = {
        1: "January 2026", 2: "February 2026", 3: "March 2026",
        4: "April 2026", 5: "May 2026", 6: "June 2026",
        7: "July 2026", 8: "August 2026", 9: "September 2026",
        10: "October 2026", 11: "November 2026", 12: "December 2026"
    }
    target_month = st.sidebar.slider("3. Target Month to Predict ", min_value=1, max_value=12, value=6,
                                     format="%d")

    # ==========================================
    #              MAIN DASHBOARD
    # ==========================================
    st.title("🍎 Malaysian Food Price Insights Dashboard")
    st.markdown("---")

    # Overall Display
    st.subheader("📊 Market Overview Indicators ")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📊 Total Price Records Checked", value=f"{len(df):,}")
    with col2:
        st.metric(label="📍 Monitored Jurisdictions", value=len(states))
    with col3:
        st.metric(label="🍏 Monitored Commodities", value=len(items))

    st.markdown("---")

    st.subheader("🎯 Intelligence Prediction & Market Drivers Report")

    result = predict_future_price(df, selected_item, selected_state, target_month)

    if result:
        pred_p, hist_p, slope, trend, reasons = result

        rep_col1, rep_col2 = st.columns(2)

        with rep_col1:
            st.info(f"**Current Scope:**\n"
                    f"* 📍 **State:** {selected_state} | 🍎 **Item:** {selected_item}\n"
                    f"* 📅 **Target Forecasting Horizon:** {month_names[target_month]}")


            st.warning(f"**Baseline Mathematical Analysis:**\n"
                       f"* 🕒 Average Monthly Price (Mac-May): RM {hist_p:.2f}\n"
                       f"* 📈 Slope: `{slope}`\n"
                       f"* 🚨 Trend: **{trend}**")

            # Display why price change
            st.markdown("#### 💡 Market Driver Breakdown ")
            for r in reasons:
                if "🌧️" in r or "🧧" in r or "🌙" in r:
                    st.error(r)
                elif "🏛️" in r:
                    st.info(r)
                else:
                    st.success(r)

        with rep_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='background-color:#1E3A8A; padding:30px; border-radius:15px; text-align:center; color:white;'>"
                f"<h2 style='color:white; margin:0;'>🌟 SMART PREDICTED PRICE 🌟</h2>"
                f"<p style='font-size:48px; font-weight:bold; margin:10px 0;'>RM {pred_p:.2f}</p>"
                f"<p style='font-size:14px; margin:0; opacity:0.8;'>Adjusted weighted estimation for {month_names[target_month]}</p>"
                f"</div>",
                unsafe_allow_html=True
            )

            st.markdown("##### 📉 Historical Price Trace Timeline :")
            historical_chart_data = df[(df['item'] == selected_item) & (df['state'] == selected_state)]
            if not historical_chart_data.empty:
                chart_df = historical_chart_data.set_index('date')[['avg_price']]
                st.line_chart(chart_df)
    else:
        st.info("No sufficient historical logs found for this specific market configuration.")
else:
    st.error("Dataset load error. Please check your data repository.")