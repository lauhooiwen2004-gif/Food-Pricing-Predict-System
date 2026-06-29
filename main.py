import streamlit as st
import pandas as pd
from function import load_price_data, get_unique_states, get_unique_items, predict_future_price

# 1. 设置网页基础配置（阔屏模式）
st.set_page_config(page_title="Malaysia Food Price Intelligence System", page_icon="🏛️", layout="wide")


@st.cache_data
def get_data():
    return load_price_data()


df = get_data()

if df is not None:
    # 提取全局唯一列表
    states = get_unique_states(df)
    items = get_unique_items(df)

    # 建立月份映射映射
    month_names = {
        1: "January 2026", 2: "February 2026", 3: "March 2026",
        4: "April 2026", 5: "May 2026", 6: "June 2026",
        7: "July 2026", 8: "August 2026", 9: "September 2026",
        10: "October 2026", 11: "November 2026", 12: "December 2026"
    }

    # ====================================================
    #          Title and Navigation
    # ====================================================
    st.title("🏛️ Malaysian Food Price Intelligence & Forecasting Platform")
    st.markdown("*Powered by Official KPDN PriceCatcher Dataset & Advanced OLS Analytics Engine*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "📊 Macro Market Overview",
        "🎯 Intelligent Price Forecasting Engine",
        "🔍 Granular Dataset Explorer"
    ])

    # ====================================================
    #      TAB 1: Market Overview
    # ====================================================
    with tab1:
        st.subheader("📈 National Food Supply Core Indicators")

        # 1. 大盘核心指标卡片
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(label="📊 Cumulative Price Logs Analyzed", value=f"{len(df):,}")
        with m_col2:
            st.metric(label="📍 Active Monitored States/Jurisdictions", value=len(states))
        with m_col3:
            st.metric(label="🍏 Total Monitored Food Items (Wide Range)", value=len(items))

        st.markdown("<br>", unsafe_allow_html=True)


        st.markdown("#### 🚨 Real-time Market Extremes & Price Alerts")
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]

        if not latest_data.empty:
            highest_row = latest_data.loc[latest_data['avg_price'].idxmax()]
            lowest_row = latest_data.loc[latest_data['avg_price'].idxmin()]

            alert_col1, alert_col2 = st.columns(2)
            with alert_col1:
                st.error(f"🔺 **Highest Recorded Price Item:** RM {highest_row['avg_price']:.2f} / unit\n\n"
                         f"*Item: `{highest_row['item']}` | Location: `{highest_row['state']}`*")
            with alert_col2:
                st.success(f"🔻 **Lowest Recorded Price Item:** RM {lowest_row['avg_price']:.2f} / unit\n\n"
                           f"*Item: `{lowest_row['item']}` | Location: `{lowest_row['state']}`*")

        st.markdown("---")
        st.info(
            "💡 **Manager Guidance Note:** Use the tabs above to toggle between running predictive simulations (Tab 2) and reviewing raw granular enterprise databases (Tab 3).")

    # ====================================================
    #      TAB 2: Forecasting Tab
    # ====================================================
    with tab2:
        st.subheader("🎯 Predictive Simulation Modeling Workspace")


        pred_input_col, pred_report_col = st.columns([1, 2])

        with pred_input_col:
            st.markdown("##### ⚙️ Target Parameters")
            selected_state = st.selectbox("Select Target State", states, key="tab2_state")
            selected_item = st.selectbox("Select Target Food Item", items, key="tab2_item")
            target_month = st.slider("Select Target Horizon Month", min_value=1, max_value=12, value=6, format="%d",
                                     key="tab2_month")

        with pred_report_col:
            st.markdown(f"##### 📋 Forecasting Insight: {selected_item} in {selected_state}")

            result = predict_future_price(df, selected_item, selected_state, target_month)

            if result:
                pred_p, hist_p, slope, trend, reasons = result


                out_col1, out_col2 = st.columns([1, 1])
                with out_col1:
                    st.warning(f"**Baseline Trend:**\n"
                               f"* 🕒 Monthly Average Price (Mac-May): RM {hist_p:.2f}\n"
                               f"* 📈 Slope: `{slope}`\n"
                               f"* 🚨 Trend: **{trend}**")

                    st.markdown("##### 💡 Market Drivers Analysis")
                    for r in reasons:
                        if "🌧️" in r or "🧧" in r or "🌙" in r:
                            st.error(r)
                        elif "🏛️" in r:
                            st.info(r)
                        else:
                            st.success(r)

                with out_col2:
                    st.markdown(
                        f"<div style='background-color:#1E3A8A; padding:25px; border-radius:12px; text-align:center; color:white;'>"
                        f"<h3 style='color:white; margin:0; font-size:18px;'>🌟 SMART PREDICTED PRICE 🌟</h3>"
                        f"<p style='font-size:42px; font-weight:bold; margin:10px 0;'>RM {pred_p:.2f}</p>"
                        f"<p style='font-size:13px; margin:0; opacity:0.8;'>Adjusted for {month_names[target_month]}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )


                    historical_chart_data = df[(df['item'] == selected_item) & (df['state'] == selected_state)].copy()
                    if not historical_chart_data.empty:
                        chart_df = historical_chart_data[['date', 'avg_price']].copy()
                        chart_df.columns = ['Date', 'Market Price']
                        pred_date = pd.to_datetime(f"2026-{target_month:02d}-15")
                        if pred_date > chart_df['Date'].max():
                            pred_point = pd.DataFrame({'Date': [pred_date], 'Market Price': [pred_p]})
                            chart_df = pd.concat([chart_df, pred_point], ignore_index=True)
                        chart_df = chart_df.set_index('Date')
                        st.line_chart(chart_df, height=200)
            else:
                st.info("No sufficient records found for this market segment combination.")

    # ====================================================
    #      TAB 3: RAW DATA
    # ====================================================
    with tab3:
        st.subheader("🔍 Interrogate Complete Parquet Database")
        st.markdown("Filter and audit the raw, underlying data stream compiled by `clean_data.py`.")

        # filter to find data
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            filter_state = st.multiselect("Filter by State(s)", states, default=None, placeholder="Show All States")
        with exp_col2:
            filter_item = st.multiselect("Filter by Food Item(s)", items, default=None, placeholder="Show All Items")


        explorer_df = df.copy()
        if filter_state:
            explorer_df = explorer_df[explorer_df['state'].isin(filter_state)]
        if filter_item:
            explorer_df = explorer_df[explorer_df['item'].isin(filter_item)]


        st.markdown(f"Total matching records：`{len(explorer_df):,}` ")
        st.dataframe(explorer_df[['date', 'item', 'state', 'avg_price']], use_container_width=True, hide_index=True)

else:
    st.error("Severe Error: Ingestion data framework failed to initialize Parquet tables.")