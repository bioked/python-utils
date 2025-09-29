# --- Standard libs ---
import sys          # for command-line args and exit codes
import json         # for pretty-printing small JSON bits
import argparse     # for command-line options
from typing import Optional, Tuple  # for clear return types

# --- Third-party ---
# You'll need this in your venv:  pip install requests
import requests

# --- API endpoints (constants so they're easy to change/test) ---
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"   # name -> lat/lon
WX_URL  = "https://api.open-meteo.com/v1/forecast"           # weather by lat/lon


def geocode_city(city: str) -> Optional[Tuple[float, float, str]]:
    """
    Turn a city name into (lat, lon, resolved_name).
    Returns None if not found or on network failure.

    Why separate this into a function?
    - Single responsibility: makes testing and reuse easier.
    - If we ever swap APIs, only this function changes.
    """
    try:
        # requests.get builds a URL with query params and performs HTTP GET.
        # Under the hood: opens TCP connection, sends headers, receives bytes.
        r = requests.get(GEO_URL, params={"name": city, "count": 1, "language": "en"})
        r.raise_for_status()  # raises on 4xx/5xx so we don't silently continue
        data = r.json()       # bytes -> text -> JSON decode -> Python dict/list/bools/nums
        results = data.get("results") or []
        if not results:
            return None
        top = results[0]
        # Build a friendly display name, e.g., "Berlin, Germany"
        name = ", ".join([p for p in [top.get("name"), top.get("country")] if p])
        return top["latitude"], top["longitude"], name
    except requests.RequestException as e:
        # Keep side effects (printing) at the edges; return None to signal failure.
        print(f"Network error during geocoding: {e}", file=sys.stderr)
        return None


def fetch_weather(lat: float, lon: float) -> Optional[dict]:
    """
    Fetch current weather + hourly temps.
    Returns the JSON payload (dict) or None on failure.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "temperature_2m",
        "forecast_days": 1,     # limit payload size/speed for a tiny script
        "timezone": "auto"      # server picks a sensible tz based on coords
    }
    try:
        r = requests.get(WX_URL, params=params)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"Network error during weather fetch: {e}", file=sys.stderr)
        return None

def pretty_print_weather(payload: dict, resolved_name: str, hours: int):
    """
    Print a human-friendly summary and a peek at structure.
    Why print? In early scripts, printing is the simplest 'UI' for learning.
    """
    cw = payload.get("current_weather", {})
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])[:hours]
    temps = hourly.get("temperature_2m", [])[:hours]

    # A compact, readable one-liner snapshot
    print(f"\nWeather for: {resolved_name}")
    print(
        f"Now: {cw.get('temperature')}°C, wind {cw.get('windspeed')} km/h, "
        f"dir {cw.get('winddirection')}°, time {cw.get('time')}"
    )

    print("\nNext hours (temperature_2m):")
    for t, temp in zip(times, temps):
        print(f"  {t}  ->  {temp}°C")

    # This 'raw keys' dump builds your mental model of the JSON shape
    print("\n--- Raw (truncated) JSON keys ---")
    print(json.dumps(
        {k: ("<big object>" if isinstance(v, (dict, list)) else v)
         for k, v in payload.items()},
        indent=2
    ))


def main() -> None:
    """
    Program entrypoint.
    Pattern to memorize:
      - read args
      - fetch data (fail fast)
      - transform/pretty print
      - exit with code (0=ok, nonzero=problem)
    """
    parser = argparse.ArgumentParser(description="Fetch weather for a city")
    parser.add_argument("city", nargs="*", default=["Berlin"],
        	            help="City name (default: Berlin)")
    parser.add_argument("--hours", type=int, default=12,
        	            help="How many future hours to show (default: 12)")
    args = parser.parse_args()

    city = " ".join(args.city)
    hours = args.hours

    geo = geocode_city(city)
    if not geo:
        print(f"Could not geocode '{city}'. Try a different name.", file=sys.stderr)
        sys.exit(1)  # nonzero exit: signals failure to the shell

    lat, lon, resolved_name = geo

    payload = fetch_weather(lat, lon)
    if not payload:
        print("Failed to retrieve weather.", file=sys.stderr)
        sys.exit(2)

    pretty_print_weather(payload, resolved_name, hours)


# Standard Python boilerplate so the file can be imported without running main()
if __name__ == "__main__":
    main()
