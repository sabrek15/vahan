# vahan/charts.py
import streamlit as st
import plotly.express as px
import pandas as pd

def bar_from_df(df, title="", index_col="label", value_col="value"):
    if df is None or df.empty:
        st.info(f"No data for {title or 'bar chart'}.")
        return
    st.subheader(title)
    st.bar_chart(df.set_index(index_col)[value_col])

def pie_from_df(df, title="", names="label", values="value", donut=True):
    if df is None or df.empty:
        st.info(f"No data for {title or 'pie chart'}.")
        return
    st.subheader(title)
    fig = px.pie(df, names=names, values=values, hole=0.4 if donut else 0)
    st.plotly_chart(fig, use_container_width=True)

def line_from_trend(df, title="Monthly registration trend"):
    if df is None or df.empty:
        st.info("No trend data.")
        return
    if df["date"].isna().any():
        st.info("Some dates could not be parsed — plotting valid points only.")
    d = df.dropna(subset=["date"]).sort_values("date")
    if d.empty:
        st.info("No valid dates to plot.")
        return
    st.subheader(title)
    st.line_chart(d.set_index("date")["value"])

def show_metrics(latest_yoy=None, latest_qoq=None):
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Latest YoY%", f"{latest_yoy:.1f}%" if latest_yoy is not None else "n/a")
    with c2:
        st.metric("Latest QoQ%", f"{latest_qoq:.1f}%" if latest_qoq is not None else "n/a")

def show_tables(yoy_df=None, qoq_df=None):
    c1, c2 = st.columns(2)
    with c1:
        if yoy_df is not None and not yoy_df.empty:
            st.markdown("YoY% by month")
            st.dataframe(yoy_df.tail(12), use_container_width=True)
    with c2:
        if qoq_df is not None and not qoq_df.empty:
            tmp = qoq_df.copy()
            if "date" in tmp and isinstance(tmp["date"].iloc[0], pd.Timestamp):
                tmp["Quarter"] = tmp["date"].dt.to_period("Q").astype(str)
            st.markdown("QoQ% by quarter")
            st.dataframe(tmp[["Quarter","value","QoQ%"]] if "Quarter" in tmp else tmp, use_container_width=True)
