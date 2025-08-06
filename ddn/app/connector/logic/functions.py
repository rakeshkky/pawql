"""
functions.py

This is an example of how you can use the Python SDK's built-in Function connector to easily write Python code.
When you add a Python Lambda connector to your Hasura project, this file is generated for you!

In this file you'll find code examples that will help you get up to speed with the usage of the Hasura lambda connector.
If you are an old pro and already know what is going on you can get rid of these example functions and start writing your own code.
"""

# from hasura_ndc.instrumentation import (
#     with_active_span,
# )  # If you aren't planning on adding additional tracing spans, you don't need this!
# from opentelemetry.trace import (
#     get_tracer,
# )  # If you aren't planning on adding additional tracing spans, you don't need this either!
from hasura_ndc import start
from hasura_ndc.function_connector import FunctionConnector
from pydantic import (
    BaseModel,
    Field,
)  # You only need this import if you plan to have complex inputs/outputs, which function similar to how frameworks like FastAPI do
import asyncio  # You might not need this import if you aren't doing asynchronous work
from hasura_ndc.errors import UnprocessableContent
from typing import Annotated
import pgeocode
import openmeteo_requests
import requests_cache
from retry_requests import retry

connector = FunctionConnector()


@connector.register_query
def get_coordinates(
    zip_code: str = Field(..., description="The zip code to get coordinates for")
) -> tuple[float, float]:
    """Get latitude and longitude coordinates for a given zip code using pgeocode library."""
    try:
        # Initialize the geocoder for US zip codes
        nomi = pgeocode.Nominatim("us")

        # Get location data for the zip code
        location = nomi.query_postal_code(zip_code)

        # Check if the location was found
        if location is None or location.empty or location.isna().all():
            raise UnprocessableContent(
                message=f"Zip code '{zip_code}' not found",
                details={"zip_code": zip_code, "error": "Invalid or unknown zip code"},
            )

        # Extract latitude and longitude
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])

        # Check if coordinates are valid (not NaN)
        if latitude != latitude or longitude != longitude:  # NaN check
            raise UnprocessableContent(
                message=f"No coordinates found for zip code '{zip_code}'",
                details={"zip_code": zip_code, "error": "Coordinates not available"},
            )

        return (latitude, longitude)

    except Exception as e:
        if isinstance(e, UnprocessableContent):
            raise e
        raise UnprocessableContent(
            message=f"Error getting coordinates for zip code '{zip_code}': {str(e)}",
            details={"zip_code": zip_code, "error": str(e)},
        )


class WeatherInfo(BaseModel):
    is_day: bool = Field(..., description="Whether it is day or not")
    temperature_c: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity in percentage")
    wind_speed_kph: float = Field(..., description="Wind speed in kilometers per hour")
    wind_direction: float = Field(..., description="Wind direction in degrees")
    precipitation_mm: float = Field(..., description="Precipitation in millimeters")


@connector.register_query
async def fetch_weather(
    latitude: float = Field(..., description="The latitude to fetch weather for"),
    longitude: float = Field(..., description="The longitude to fetch weather for"),
) -> WeatherInfo:
    """Fetch current weather data for given coordinates"""
    try:
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Make sure all required weather variables are listed here
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "rain",
                "showers",
                "snowfall",
                "is_day",
            ],
            "forecast_days": 1,
        }

        responses = openmeteo.weather_api(url, params=params)

        # Process first location
        response = responses[0]

        # Process current data. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_relative_humidity_2m = current.Variables(1).Value()
        # Skip apparent_temperature (index 2) as we don't use it
        current_wind_speed_10m = current.Variables(3).Value()
        current_wind_direction_10m = current.Variables(4).Value()
        current_precipitation = current.Variables(5).Value()
        current_rain = current.Variables(6).Value()
        current_showers = current.Variables(7).Value()
        current_snowfall = current.Variables(8).Value()
        current_is_day = current.Variables(9).Value()

        # Calculate total precipitation (rain + showers + snowfall)
        total_precipitation = (
            current_precipitation + current_rain + current_showers + current_snowfall
        )

        return WeatherInfo(
            is_day=bool(current_is_day),
            temperature_c=float(current_temperature_2m),
            humidity=float(current_relative_humidity_2m),
            wind_speed_kph=float(current_wind_speed_10m * 3.6),  # Convert m/s to km/h
            wind_direction=float(current_wind_direction_10m),
            precipitation_mm=float(total_precipitation),
        )

    except Exception as e:
        raise UnprocessableContent(
            message=f"Error fetching weather data: {str(e)}",
            details={"latitude": latitude, "longitude": longitude, "error": str(e)},
        )


if __name__ == "__main__":
    start(connector)
