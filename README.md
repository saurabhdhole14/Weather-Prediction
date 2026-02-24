Weather Bot 🌤️
A resilient, production-ready Python command-line tool that fetches real-time weather data and forecasts for any city worldwide using the Open-Meteo API.

Features
Resilient Networking: Built with a custom requests.Session that implements exponential backoff and automatic retries for common server errors (429, 500, 502, 503, 504).

Geocoding Integration: Automatically converts city names into precise latitude and longitude coordinates.

Comprehensive Data: Provides current temperature, "feels like" temperature, humidity, wind speed, and daily summaries (Min/Max temp and precipitation).

User-Friendly Output: Maps technical WMO weather codes to human-readable descriptions.

No API Key Required: Uses the free tier of Open-Meteo for easy setup.

Installation
Clone the repository:

Bash
git clone https://github.com/your-username/weather-bot-python.git
cd weather-bot-python
Create and activate a virtual environment:

Bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
Install dependencies:

Bash
pip install requests urllib3
Usage
Run the script from your terminal:

Bash
python Weather_prediction.py
Enter any city name (e.g., Nagpur, Guwahati, or London) when prompted to receive the latest weather report.

Project Structure
Weather_prediction.py: The main script containing the logic for session building, geocoding, and weather fetching.

.venv/: (Ignored) Python virtual environment.

README.md: Project documentation.

Technical Details
The core of this bot's reliability comes from the build_session function, which ensures that temporary network glitches don't crash the application:

Python
retry = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(["GET"])
)

OUTPUT:
<img width="365" height="181" alt="image" src="https://github.com/user-attachments/assets/3f0483fb-005a-4206-9108-ee23450d5432" />
