import requests
from datetime import datetime, timezone


def convert_unix_to_readable_date(unix_timestamp):
    """
    Convert a Unix timestamp to a human-readable date in the format 'YYYY-MM-DD'.
    :param unix_timestamp: Unix timestamp (int)
    :return: A string representing the date in 'YYYY-MM-DD' format
    """
    return datetime.fromtimestamp(unix_timestamp, timezone.utc).strftime('%Y-%m-%d')


def kelvin_to_fahrenheit(kelvin_temp):
    """
    Convert a temperature from Kelvin to Fahrenheit.
    :param kelvin_temp: Temperature in Kelvin (float)
    :return: Temperature in Fahrenheit, rounded to two decimal places
    """
    return round((kelvin_temp - 273.15) * 9 / 5 + 32, 2)


def celsius_to_fahrenheit(celsius_temp):
    """
    Convert a temperature from Celsius to Fahrenheit.
    :param celsius_temp: Temperature in Celsius(float)
    :return: Temperature in Fahrenheit, rounded to the nearest integer.
    """
    return round((celsius_temp * 9/5) + 32)


def get_current_weather(city_name):
    """
    Fetch the current weather data for a given city.
    :param city_name: Name of the city(str)
    :return: A tuple containing the weather data and coordinates if successful, (None, None) otherwise
    """
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    current_weather = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(current_weather)

    if response.status_code == 200:
        weather_data = response.json()
        if 'coord' in weather_data:
            coordinates = weather_data['coord']
            return weather_data, coordinates
        else:
            return None, None
    else:
        return None, None


def get_weather_forecast(coords):
    """
    Fetch the weather forecast data based on given coordinates.
    :param coords: Dictionary containing 'lat' and 'lon' as latitude and longitude.
    :return: Forecast data if successful, None otherwise.
    """
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    lat = coords['lat']
    lon = coords['lon']
    weather_forecast = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=hourly,minutely&appid={api_key}'
    response = requests.get(weather_forecast)
    if response.status_code == 200:
        forecast_data = response.json()
        return forecast_data
    else:
        return None


def clean_weather_data(weather_data):
    """
    Clean and reformat the raw weather data from the API.
    :param weather_data: Raw weather data(dict)
    :return: Cleaned and reformatted weather data (dict)
    """
    description = weather_data['weather'][0].get('description')
    temp = celsius_to_fahrenheit(weather_data['main'].get('temp'))
    city_name = weather_data['name']
    revised_data = {
        'temp': temp,
        'weather description': description,
        'city': city_name
    }
    return revised_data


def clean_forecast_data(forecast_data):
    """
    Clean and reformat the raw forecast data from the API
    :param forecast_data: Raw forecast data(dict)
    :return: List of dictionaries with cleaned and reformatted forecast data
    """
    cleaned_forecast = []
    for day in forecast_data['daily']:
        day_data = {
            'date': convert_unix_to_readable_date(day['dt']),
            'temperature': {
                'day': kelvin_to_fahrenheit(day['temp']['day']),
                'min': kelvin_to_fahrenheit(day['temp']['min']),
                'max': kelvin_to_fahrenheit(day['temp']['max']),
                'night': kelvin_to_fahrenheit(day['temp']['night']),
                'evening': kelvin_to_fahrenheit(day['temp']['eve']),
                'morning': kelvin_to_fahrenheit(day['temp']['morn'])
            },
            'feels_like': kelvin_to_fahrenheit(day['feels_like']['day']),
            'weather_description': day['weather'][0]['description'],
            'wind_speed': day['wind_speed']
        }
        cleaned_forecast.append(day_data)
    return cleaned_forecast


def display_forecast(cleaned_forecast):
    """
    Display the weather forecast in a readable format.
    :param cleaned_forecast: List of dictionaries containing the cleaned forecast data
    """
    for day in cleaned_forecast:
        print(f"Date: {day['date']}")
        print(f"Temperature: {day['temperature'].get('day')} degrees")
        print(f"Daily Low: {day['temperature'].get('min')} degrees")
        print(f"Daily High: {day['temperature'].get('max')} degrees")
        print(f"Morning Temperature: {day['temperature'].get('morning')} degrees")
        print(f"Evening Temperature: {day['temperature'].get('evening')} degrees")
        print(f"Night Temperature: {day['temperature'].get('night')} degrees")
        print(f"It Feels Like: {day['feels_like']} degrees")
        print(f"Weather Description: {day['weather_description']}")
        print(f"Wind Speed: {day['wind_speed']} mph")
        print("------------------------------")


def display_weather(revised_data):
    """
    Display the current weather in a readable format.
    :param revised_data: Dictionary containing the cleaned current weather data
    """
    print(f"Temperature: {revised_data['temp']} degrees")
    print(f"Weather Description: {revised_data['weather description']}")
    print(f"City: {revised_data['city']}")
    print()


def main():
    """
     Main function to run the weather application.
    It prompts the user to enter a city and choose between viewing the current weather,
    a weather forecast, or exiting the program.
    """
    while True:
        city = input('Enter a city (or type "exit" to quit): ')
        if city.lower() == 'exit':
            print("Exiting program.")
            break

        raw_weather_data, coords = get_current_weather(city)
        if not raw_weather_data or not coords:
            print("City not found. Please enter a valid city name.")
            continue

        while True:
            choice = input("\nChoose an option:\n1. Current Weather\n2. Weather Forecast\n3. Exit\nSelect (1/2/3): ")
            if choice == '1':
                cleaned_weather_data = clean_weather_data(raw_weather_data)
                print("\nCurrent Weather Data:")
                display_weather(cleaned_weather_data)
            elif choice == '2':
                forecast = get_weather_forecast(coords)
                if forecast:
                    cleaned_forecast = clean_forecast_data(forecast)
                    print("\nWeather Forecast Data:")
                    display_forecast(cleaned_forecast)
                else:
                    print("Unable to retrieve weather forecast.")
            elif choice == '3':
                print("Returning to city selection...")
                break
            else:
                print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
