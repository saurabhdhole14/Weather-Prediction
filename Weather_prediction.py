import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 1. Global Configuration
TIMEOUT = 10  # Standardized timeout for all API calls

def build_session(retries=3, backoff=0.5):
    """
    Creates a resilient session to handle network glitches or busy servers.
    """
    s = requests.Session()
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    
    # Mount the adapter to both HTTP and HTTPS
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

def geocode_city(session, city: str): 
    """
    Converts city name into latitude and longitude coordinates.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    
    try:
        r = session.get(url, params=params, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        print("⌛ Geocoding timeout. Try again.")
        return None
    except requests.exceptions.RequestException as e:
        print("❌ Network error in geocoding:", e)
        return None

    if r.status_code != 200:
        print(f"❌ Geocoding failed. HTTP {r.status_code}")
        return None

    data = r.json()
    results = data.get("results", [])
    if not results:
        print(f"😶 City '{city}' not found. Try checking the spelling.")
        return None

    top = results[0]
    return {
        "name": top.get("name", city),
        "country": top.get("country", ""),
        "lat": top.get("latitude"),
        "lon": top.get("longitude"),
        "timezone": top.get("timezone", "auto"),
    }

def get_weather(session, lat, lon, timezone="auto"):
    """
    Fetches current and daily forecast data for specific coordinates.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": timezone,
        "forecast_days": 1
    }

    try:
        r = session.get(url, params=params, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        print("⌛ Weather API timeout. Try again.")
        return None
    except requests.exceptions.RequestException as e:
        print("❌ Network error in weather:", e)
        return None
    
    if r.status_code != 200:
        print(f"❌ Weather fetch failed. HTTP {r.status_code}")
        return None
        
    return r.json()

def wmo_code_to_text(code: int) -> str:
    """
    Maps WMO weather codes to human-readable strings.
    """
    mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Rain showers",
        95: "Thunderstorm",
    }
    return mapping.get(code, f"Condition {code}")

def print_weather(city_info, weather_json):
    """
    Formats and displays the weather information.
    """
    cur = weather_json.get("current", {})
    daily = weather_json.get("daily", {})

    # Helper function to safely extract the first item from daily lists
    def get_safe_daily(key):
        val = daily.get(key)
        return val[0] if isinstance(val, list) and len(val) > 0 else "N/A"

    temp = cur.get("temperature_2m", "N/A")
    feels = cur.get("apparent_temperature", "N/A")
    hum = cur.get("relative_humidity_2m", "N/A")
    wind = cur.get("wind_speed_10m", "N/h")
    code = cur.get("weather_code", 0)

    tmax = get_safe_daily("temperature_2m_max")
    tmin = get_safe_daily("temperature_2m_min")
    rain = get_safe_daily("precipitation_sum")

    print("\n" + "="*20 + " WEATHER BOT " + "="*20 + "\n")
    print(f"📍 Location: {city_info['name']}, {city_info['country']}")
    print(f"🌤️ Condition: {wmo_code_to_text(code)}")
    print(f"🌡️ Current: {temp}°C (Feels like: {feels}°C)")
    print(f"💧 Humidity: {hum}%")
    print(f"💨 Wind: {wind} km/h")
    print(f"📅 Today: Low {tmin}°C | High {tmax}°C | Rain {rain} mm")
    print("\n" + "="*53 + "\n")

def main():
    session = build_session()

    print("📩 Resilient Weather Bot")
    city = input("Enter city name: ").strip()

    if not city:
        print("❌ City name cannot be empty.")
        return

    # Step 1: Geocoding
    city_info = geocode_city(session, city)
    if not city_info:
        return

    # Step 2: Weather Fetching
    weather = get_weather(session, city_info["lat"], city_info["lon"], timezone=city_info["timezone"])
    if not weather:
        return

    # Step 3: Output
    print_weather(city_info, weather)

if __name__ == "__main__":
    main()