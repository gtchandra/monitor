import requests
from .cache import get as cached

_WX_CODES = {
    "113": "Sunny", "116": "Pt. Cloudy", "119": "Cloudy", "122": "Overcast",
    "143": "Mist", "176": "Patchy Rain", "179": "Patchy Snow", "182": "Patchy Sleet",
    "185": "Patchy Freezing Drizzle", "200": "Thundery Outbreaks", "227": "Blowing Snow",
    "230": "Blizzard", "248": "Fog", "260": "Freezing Fog", "263": "Patchy Light Drizzle",
    "266": "Light Drizzle", "281": "Freezing Drizzle", "284": "Heavy Freezing Drizzle",
    "293": "Patchy Light Rain", "296": "Light Rain", "299": "Moderate Rain",
    "302": "Heavy Rain", "305": "Heavy Rain", "308": "Very Heavy Rain",
    "311": "Light Sleet", "314": "Moderate Sleet", "317": "Light Sleet",
    "320": "Moderate Snow", "323": "Patchy Light Snow", "326": "Light Snow",
    "329": "Patchy Moderate Snow", "332": "Moderate Snow", "335": "Patchy Heavy Snow",
    "338": "Heavy Snow", "350": "Ice Pellets", "353": "Light Rain Shower",
    "356": "Moderate Rain Shower", "359": "Torrential Rain Shower",
    "362": "Light Sleet Shower", "365": "Moderate Sleet Shower",
    "368": "Light Snow Shower", "371": "Moderate Snow Shower",
    "374": "Light Ice Pellet Shower", "377": "Moderate Ice Pellet Shower",
    "386": "Patchy Light Rain + Thunder", "389": "Moderate Rain + Thunder",
    "392": "Patchy Light Snow + Thunder", "395": "Moderate Snow + Thunder",
}

def _fetch(location):
    r = requests.get(
        f"http://wttr.in/{location}",
        params={"format": "j1"},
        timeout=5,
        headers={"User-Agent": "monitor-dashboard/1.0"},
    )
    r.raise_for_status()
    data = r.json()
    cur = data["current_condition"][0]
    today = data["weather"][0]
    tomorrow = data["weather"][1]

    def desc(day):
        code = day["hourly"][4]["weatherCode"]
        return _WX_CODES.get(code, f"Code {code}")

    return {
        "temp_c": cur["temp_C"],
        "feels_c": cur["FeelsLikeC"],
        "desc": _WX_CODES.get(cur["weatherCode"], cur["weatherCode"]),
        "wind_kmph": cur["windspeedKmph"],
        "today_max": today["maxtempC"],
        "today_min": today["mintempC"],
        "today_desc": desc(today),
        "tomorrow_max": tomorrow["maxtempC"],
        "tomorrow_min": tomorrow["mintempC"],
        "tomorrow_desc": desc(tomorrow),
    }

def get(location):
    return cached(f"weather:{location}", ttl=600, fetch_fn=lambda: _fetch(location))
