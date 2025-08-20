# app/streamlit_app.py
import streamlit as st
import pandas as pd
from datetime import date

from vahan.api import build_params, get_json
from vahan.parsing import to_df, normalize_trend, parse_duration_table, parse_top5_revenue, parse_revenue_trend
from vahan.metrics import compute_yoy, compute_qoq
from vahan.charts import bar_from_df, pie_from_df, line_from_trend, show_metrics, show_tables

st.set_page_config(page_title="Vahan Registrations — Investor Dashboard", layout="wide")
st.title("Vahan Registrations — Investor Dashboard")
# st.caption("Public JSON endpoints used by the official Vahan dashboard. If parsing fails, open debug expanders and adjust key mapping in vahan/parsing.py.")

# Sidebar filters
today = date.today()
def to_df(json_obj, label_keys=("label",), value_key="value"):
    # Handle case where 'labels' and 'data' are parallel arrays
    if "labels" in json_obj and "data" in json_obj:
        labels = json_obj["labels"]
        values = json_obj["data"]
        # Defensive: ensure same length
        if len(labels) == len(values):
            return pd.DataFrame({"label": labels, "value": values})
        else:
            # fallback: truncate to shortest
            min_len = min(len(labels), len(values))
            return pd.DataFrame({"label": labels[:min_len], "value": values[:min_len]})
    # ...existing code for list of dicts...
    data = json_obj.get("data", json_obj)
    if isinstance(data, dict):
        data = [data]
    rows = []
    for item in data:
        label = None
        for k in label_keys:
            if k in item:
                label = item[k]
                break
        if label is None and label_keys:
            label = item.get(label_keys[0], None)
        value = item.get(value_key, None)
        if value is None:
            for vk in ("count", "value", "total"):
                if vk in item:
                    value = item[vk]
                    break
        if label is not None and value is not None:
            rows.append({"label": label, "value": value})
    return pd.DataFrame(rows)
default_from_year = max(2017, today.year - 1)

st.sidebar.header("Filters")
from_year = st.sidebar.number_input("From Year", min_value=2012, max_value=today.year, value=default_from_year)
to_year = st.sidebar.number_input("To Year", min_value=from_year, max_value=today.year, value=today.year)
state_code = st.sidebar.text_input("State Code (blank=All-India)", value="")
rto_code = st.sidebar.text_input("RTO Code (0=aggregate)", value="0")
vehicle_classes = st.sidebar.text_input("Vehicle Classes (e.g., 2W,3W,4W if accepted)", value="")
vehicle_makers = st.sidebar.text_input("Vehicle Makers (comma-separated or IDs)", value="")
time_period = st.sidebar.selectbox("Time Period", options=[0,1,2], index=0)
fitness_check = st.sidebar.selectbox("Fitness Check", options=[0,1], index=0)
vehicle_type = st.sidebar.text_input("Vehicle Type (optional)", value="")

params_common = build_params(
    from_year, to_year,
    state_code=state_code, rto_code=rto_code,
    vehicle_classes=vehicle_classes, vehicle_makers=vehicle_makers,
    time_period=time_period, fitness_check=fitness_check, vehicle_type=vehicle_type
)

# 1) Category distribution
with st.spinner("Fetching category distribution..."):
    cat_json, cat_url = get_json("vahandashboard/categoriesdonutchart", params_common)

# Remove or comment out these lines for the category section:
# st.caption(f"Category API: {cat_url}")
# with st.expander("Debug: categories JSON"):
#     st.json(cat_json)

# Keep these lines to display the charts:
df_cat = to_df(cat_json)
col1, col2 = st.columns(2)
with col1:
    bar_from_df(df_cat, title="Category distribution (bar)")
with col2:
    pie_from_df(df_cat, title="Category distribution (pie)", donut=True)

# # 2) Top makers
# with st.spinner("Fetching top makers..."):
#     mk_json, mk_url = get_json("vahandashboard/top5Makerchart", params_common)
# st.caption(f"Top Makers API: {mk_url}")
# with st.expander("Debug: top makers JSON"):
#     st.json(mk_json)
# df_mk = to_df(mk_json, label_keys=("makerName","manufacturer","name","label"))
# bar_from_df(df_mk, title="Top makers by registrations")

# 3) Time series trend + YoY/QoQ
with st.spinner("Fetching time series trend..."):
    tr_json, tr_url = get_json("vahandashboard/vahanyearwiseregistrationtrend", params_common)
# st.caption(f"Trend API: {tr_url}")
# with st.expander("Debug: trend JSON"):
#     st.json(tr_json)

try:
    df_trend = normalize_trend(tr_json)
except Exception as e:
    st.error(f"Trend parsing failed: {e}")
    df_trend = pd.DataFrame(columns=["date","value"])

line_from_trend(df_trend)

yoy_df = compute_yoy(df_trend) if not df_trend.empty else pd.DataFrame()
qoq_df = compute_qoq(df_trend) if not df_trend.empty else pd.DataFrame()

latest_yoy = yoy_df["YoY%"].dropna().iloc[-1] if not yoy_df.empty and yoy_df["YoY%"].dropna().size else None
latest_qoq = qoq_df["QoQ%"].dropna().iloc[-1] if not qoq_df.empty and qoq_df["QoQ%"].dropna().size else None
show_metrics(latest_yoy, latest_qoq)
show_tables(yoy_df, qoq_df)

# Vehicle Registration Growth Rate - Quarterly
with st.spinner("Fetching quarterly registration growth..."):
    quarter_json, quarter_url = get_json(
        "vahandashboard/durationWiseRegistrationTable",
        {**params_common, "calendarType": 2}  # 2 for quarterly
    )
df_quarter = parse_duration_table(quarter_json)
st.subheader("Quarterly Vehicle Registration Growth")
bar_from_df(df_quarter, title="Quarterly Growth (bar)")
pie_from_df(df_quarter, title="Quarterly Growth (pie)", donut=True)

# Vehicle Registration Growth Rate - Yearly
with st.spinner("Fetching yearly registration growth..."):
    year_json, year_url = get_json(
        "vahandashboard/durationWiseRegistrationTable",
        {**params_common, "calendarType": 1}  # 1 for yearly
    )
df_year = parse_duration_table(year_json)
st.subheader("Yearly Vehicle Registration Growth")
bar_from_df(df_year, title="Yearly Growth (bar)")
pie_from_df(df_year, title="Yearly Growth (pie)", donut=True)

# Vehicle Registration Growth Rate - Monthly
with st.spinner("Fetching monthly registration growth..."):
    month_json, month_url = get_json(
        "vahandashboard/durationWiseRegistrationTable",
        {**params_common, "calendarType": 3}  # 3 for monthly
    )
df_month = parse_duration_table(month_json)
st.subheader("Monthly Vehicle Registration Growth")
bar_from_df(df_month, title="Monthly Growth (bar)")
pie_from_df(df_month, title="Monthly Growth (pie)", donut=True)

# 5) Top 5 Revenue States
with st.spinner("Fetching top 5 revenue states..."):
    top5_rev_json, top5_rev_url = get_json(
        "vahandashboard/top5chartRevenueFee", params_common
    )
df_top5_rev = parse_top5_revenue(top5_rev_json)
st.subheader("Top 5 Revenue States")
bar_from_df(df_top5_rev, title="Top 5 Revenue States (bar)")
pie_from_df(df_top5_rev, title="Top 5 Revenue States (pie)", donut=True)

# 6) Revenue Trend
with st.spinner("Fetching revenue trend..."):
    rev_trend_json, rev_trend_url = get_json(
        "vahandashboard/revenueFeeLineChart", params_common
    )
df_rev_trend = parse_revenue_trend(rev_trend_json)
st.subheader("Revenue Trend Comparison")

import altair as alt

# Plot line chart: one line per year
chart = alt.Chart(df_rev_trend).mark_line(point=True).encode(
    x=alt.X('period:O', title='Period'),
    y=alt.Y('value:Q', title='Revenue'),
    color='year:N'
).properties(
    title="Revenue Trend Comparison"
)
st.altair_chart(chart, use_container_width=True)

# 7) Downloads
with st.expander("Download CSV"):
    if not df_cat.empty:
        st.download_button("Category CSV", df_cat.to_csv(index=False), "category_distribution.csv")
    # if not df_mk.empty:
    #     st.download_button("Top makers CSV", df_mk.to_csv(index=False), "top_makers.csv")
    if not df_trend.empty:
        st.download_button("Monthly trend CSV", df_trend.to_csv(index=False), "registrations_monthly.csv")
    if not yoy_df.empty:
        st.download_button("YoY CSV", yoy_df.to_csv(index=False), "registrations_yoy.csv")
    if not qoq_df.empty:
        st.download_button("QoQ CSV", qoq_df.to_csv(index=False), "registrations_qoq.csv")
