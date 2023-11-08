# Create a Python script or web form to collect user input for travel date, start location, and destination.

import openai
import config
import requests
import json 

openai.api_key = config.OPEN_AI_API_KEY
google_places_api_key = config.GOOGLE_PLACES_API_KEY
weatherbit_api_key = config.WEATHER_BIT_API_KEY

'''
# user input testing 
user_destination = 'Seattle'

# place details testing 
lat=21.0277644
lng=105.8341598

# weather testing
place_full_name='hanoi, vn'
'''


# # CREDIT to Sentdex
user_destination = input("Enter a city: ")
model_engine = "gpt-3.5-turbo"
user_search_string = f"What city do you want to travel to?"
user_search_string2 = f"What month will you travel?"
user_search_string3 = f"What is the typical weather in {user_destination} in the month of January?"

completion = openai.ChatCompletion.create(
  model=model_engine,
  messages=[{"role": "user", "content": user_search_string3}],
  # max_tokens=30,
  n=1,
  stop=None, 
  temperature=0.5,
)
chatgpt_response = completion.choices[0].message.content
print("chatgpt_response >> ", chatgpt_response)

# message_history = []
# user_search_string = f"What is the most famous attraction in this city?"
# message_history.append({"role": "user", "content": user_search_string})
# # print("message_history only user >> ", message_history)

# message_history.append({"role": "assistant", "content": chatgpt_response})
# # print("message_history with assistant >> ", message_history)

# completion = openai.ChatCompletion.create(
#   model=model_engine,
#   messages=message_history,
# )

# chatgpt_response = completion.choices[0].message.content
# print("chatgpt_response 2 >> ", chatgpt_response)


#get google place id
def get_place_id(user_dest):
  google_place_id_url=f'https://maps.googleapis.com/maps/api/geocode/json?address={user_dest}&key={google_places_api_key}'
  response_google_place_id = requests.get(google_place_id_url)
  converted_place_id_response = json.loads(response_google_place_id.text)
  retreived_place_id = converted_place_id_response['results'][0]['place_id']
  return retreived_place_id


#get place details 
def get_place_details(place_id):
  google_place_details_url=f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={google_places_api_key}'
  response_google_place_details = requests.get(google_place_details_url)
  converted_place_full_details_response = json.loads(response_google_place_details.text)
  retreived_place_full_details = converted_place_full_details_response['result']

  #access the desired details  
  place_full_name = retreived_place_full_details["formatted_address"]
  place_url = retreived_place_full_details["url"]
  place_lat = retreived_place_full_details['geometry']['location']['lat']
  place_lng = retreived_place_full_details['geometry']['location']['lng']
  details_list = [place_full_name, place_url, place_lat, place_lng]
  return details_list

#get restaurants within 16000 meters / 10 miles
def get_restaurants(lat,lng):
  google_nearby_restaurants_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&type=restaurant&radius=16000&key={google_places_api_key}'
  response_nearby_restaurants_search = requests.get(google_nearby_restaurants_url)
  converted_nearby_restaurants_search = json.loads(response_nearby_restaurants_search.text)
  nearby_restaurant_results = [restaurant for restaurant in converted_nearby_restaurants_search['results']]
  nearby_restaurant_results_sorted = sorted(nearby_restaurant_results, key=lambda x: x.get('rating', 0), reverse=True)

  restaurant_list = []
  for restaurant in nearby_restaurant_results_sorted:
      restaurant_list.append(f"{restaurant['name']}: {restaurant.get('rating', 'N/A')} stars")

  return restaurant_list

#get tourist attractions within 16000 meters / 10 miles
def get_attractions(lat,lng):
  google_nearby_tourist_attraction_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&type=tourist_attraction&radius=16000&key={google_places_api_key}'
  response_nearby_attraction_search = requests.get(google_nearby_tourist_attraction_url)
  converted_nearby_attractions_search = json.loads(response_nearby_attraction_search.text)
  nearby_attraction_results = [attraction for attraction in converted_nearby_attractions_search['results']]
  nearby_attraction_results_sorted = sorted(nearby_attraction_results, key=lambda x: x.get('rating', 0), reverse=True)
  attractions_list = []
  for attraction in nearby_attraction_results_sorted:
      attractions_list.append(f"{attraction['name']}: {attraction.get('rating', 'N/A')} stars")

  return attractions_list

def get_weather_data(place_name):
  #get weather data
  weatherbit_forecast_url = f'https://api.weatherbit.io/v2.0/forecast/daily?city={place_name}&key={weatherbit_api_key}'

  response_weatherbit_forecast = requests.get(weatherbit_forecast_url)
  converted_weather_response = json.loads(response_weatherbit_forecast.text)
  retreived_weather=converted_weather_response["data"][:7]
  weather_instances_list = [WeatherDay(weather_obj) for weather_obj in retreived_weather]
  
  return weather_instances_list

# CREDIT Chatgpt
class WeatherDay:
  def __init__(self, weather_object):
    self.date = weather_object.get('datetime', None)
    self.min_temp = weather_object.get('min_temp' , None)
    self.max_temp = weather_object.get('max_temp', None)
    self.description = weather_object.get('weather', None).get('description', None)

  def __str__(self):
    return f"Date: {self.date}. Degrees: {self.min_temp}-{self.max_temp}. Description: {self.description}"


if __name__ == '__main__':
  print('hi py')
  place_id = get_place_id(user_destination)
  place_details = get_place_details(place_id)
  lat, lon = place_details[2], place_details[3]
  restaurants_list = get_restaurants(lat, lon)
  attractions_list = get_attractions(lat, lon)
  # print(attractions_list)