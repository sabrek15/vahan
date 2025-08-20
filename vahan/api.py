# vahan/api.py
import requests
from urllib.parse import urlencode

BASE = "https://analytics.parivahan.gov.in/analytics/publicdashboard"
DEFAULT_TIMEOUT = 30
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}

def build_params(
    from_year, to_year, state_code="", rto_code="0",
    vehicle_classes="", vehicle_makers="", time_period=0,
    fitness_check=0, vehicle_type="", extra=None
):
    params = {
        "fromYear": from_year,
        "toYear": to_year,
        "stateCode": state_code,
        "rtoCode": rto_code,
        "vehicleClasses": vehicle_classes,
        "vehicleMakers": vehicle_makers,
        "vehicleSubCategories": "",
        "vehicleEmissions": "",
        "vehicleFuels": "",
        "timePeriod": time_period,
        "vehicleCategoryGroup": "",
        "evType": "",
        "vehicleStatus": "",
        "vehicleOwnerType": "",
        "fitnessCheck": fitness_check,
        "vehicleType": vehicle_type,
    }
    if extra:
        params.update(extra)
    return params

def get_json(path: str, params: dict, timeout=DEFAULT_TIMEOUT):
    url = f"{BASE}/{path}?{urlencode(params, doseq=True)}"
    r = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.json(), url
