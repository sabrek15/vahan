# vahan/metrics.py
import pandas as pd

def compute_yoy(df, date_col="date", value_col="value"):
    if df.empty:
        return df.assign(**{"YoY%": None})
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d = d.dropna(subset=[date_col]).set_index(date_col).sort_index()
    if d.empty:
        return df.assign(**{"YoY%": None})
    m = d[value_col].resample("MS").sum()
    yoy = (m - m.shift(12)) / m.shift(12) * 100
    return pd.DataFrame({"date": m.index, "value": m.values, "YoY%": yoy.values})

def compute_qoq(df, date_col="date", value_col="value"):
    if df.empty:
        return df.assign(**{"QoQ%": None})
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d = d.dropna(subset=[date_col]).set_index(date_col).sort_index()
    if d.empty:
        return df.assign(**{"QoQ%": None})
    q = d[value_col].resample("QS").sum()
    qoq = (q - q.shift(1)) / q.shift(1) * 100
    return pd.DataFrame({"date": q.index, "value": q.values, "QoQ%": qoq.values})

def quarter_label(ts: pd.Timestamp):
    q = (ts.month - 1) // 3 + 1
    return f"Q{q}-{ts.year}"
