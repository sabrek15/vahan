# vahan/parsing.py
import pandas as pd

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

def month_to_int(m):
    s = str(m).strip()
    if s.isdigit(): 
        return int(s)
    for fmt in ("%b", "%B"):
        try:
            return pd.to_datetime(s, format=fmt).month
        except Exception:
            pass
    return None

def normalize_trend(trend_json):
    data = trend_json
    if isinstance(data, dict):
        for k in ("data","rows","result","values","series","payload"):
            if k in data and isinstance(data[k], list):
                data = data[k]
                break
    if not isinstance(data, list):
        raise ValueError("Trend payload is not a list; inspect JSON and adjust key mapping.")

    rows = []
    for it in data:
        if not isinstance(it, dict): 
            continue
        y = it.get("year") or it.get("Year") or it.get("yr")
        m = it.get("month") or it.get("Month") or it.get("mn") or it.get("monthNo") or it.get("monthNumber")
        my = it.get("Month-Year") or it.get("monthYear") or it.get("label") or it.get("period") or it.get("monthNameYear")
        cnt = it.get("count") or it.get("value") or it.get("registrations") or it.get("total") or it.get("registeredVehicleCount")

        dt = None
        if y and m:
            mi = month_to_int(m)
            if mi:
                dt = pd.Timestamp(int(y), int(mi), 1)

        if dt is None and my:
            for fmt in ("%b-%Y","%Y-%m","%B %Y","%b %Y","%Y %b"):
                try:
                    parsed = pd.to_datetime(my, format=fmt)
                    dt = pd.Timestamp(parsed.year, parsed.month, 1)
                    break
                except Exception:
                    pass
            if dt is None:
                parsed = pd.to_datetime(str(my).replace("/", "-"), errors="coerce")
                if pd.notna(parsed):
                    dt = pd.Timestamp(parsed.year, parsed.month, 1)

        if dt is None and y:
            try:
                dt = pd.Timestamp(int(y), 1, 1)
            except Exception:
                dt = None

        if dt is not None and cnt is not None:
            try:
                val = float(str(cnt).replace(",", ""))
                rows.append({"date": dt, "value": val})
            except Exception:
                pass

    if not rows:
        raise ValueError("No trend rows parsed; check actual JSON keys.")
    return pd.DataFrame(rows).sort_values("date")

def normalize_trend(json_obj):
    # Handles parallel arrays for year-wise registration trend
    if "labels" in json_obj and "data" in json_obj:
        years = json_obj["labels"]
        values = json_obj["data"]
        min_len = min(len(years), len(values))
        if min_len == 0:
            raise ValueError("No trend rows parsed; check actual JSON keys.")
        return pd.DataFrame({
            "date": years[:min_len],
            "value": values[:min_len]
        })
    raise ValueError("No trend rows parsed; check actual JSON keys.")

def parse_duration_table(json_obj):
    # Handles list of dicts for duration-wise registration
    if isinstance(json_obj, list):
        rows = []
        for item in json_obj:
            label = item.get("yearAsString")
            if not label:
                label = str(item.get("year", ""))
            value = item.get("registeredVehicleCount", None)
            if label and value is not None:
                rows.append({"label": label, "value": value})
        return pd.DataFrame(rows)
    return pd.DataFrame(columns=["label", "value"])

def parse_top5_revenue(json_obj):
    # Handles parallel arrays for top 5 revenue states
    if "labels" in json_obj and "data" in json_obj:
        labels = json_obj["labels"]
        values = json_obj["data"]
        min_len = min(len(labels), len(values))
        return pd.DataFrame({
            "label": labels[:min_len],
            "value": values[:min_len]
        })
    return pd.DataFrame(columns=["label", "value"])

def parse_revenue_trend(json_obj):
    # Converts the revenue trend JSON to a DataFrame for plotting
    rows = []
    for year, values in json_obj.items():
        for idx, value in enumerate(values, start=1):
            rows.append({"year": year, "period": idx, "value": value})
    return pd.DataFrame(rows)
