import requests
import json
from openai import OpenAI

# OpenAI API KEY
client = OpenAI(api_key="YOUR API KEY")

with open('api_info.json', 'r') as f:
    api_info = json.load(f)

def openai_response():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.2,
        max_tokens=512,
        functions=functions,
        function_call="auto",
      # messages = [{"role": "user", "content": "You are a helpful AI assistant. What is the time and date for Turkey?"}] # For the date and time info using country name
        messages = [{"role": "user", "content": "You are a helpful AI assistant. Give me top 3 news using source, author, title, published date and url for this country code 'tr'"}] # For the news using country code
    )
    print (response.choices[0].message)
    processed_response = process_openai_response(response.choices[0].message)
    return processed_response


def process_openai_response(response_message):
    messages = []

    if response_message.function_call:
        function_call = response_message.function_call
        function_name = function_call.name
        function_args = json.loads(function_call.arguments)  # Parsing JSON string to dictionary

        if function_name == "get_current_date":
            country_name = function_args["country_name"]
            function_response = get_current_date(country_name)
            messages = [{"role": "user", "content": "You are a helpful AI assistant. What is the time and date for" + country_name}]
            messages.append({
                "role": "function",
                "name": function_name,
                "content": function_response
            })

        elif function_name == "get_top_news":
            country_code = function_args["country_code"]
            function_response = get_top_news(country_code)
            messages = [{"role": "user", "content": "You are a helpful AI assistant. Give me top 3 news using source, author, title, published date and url for this country code" + country_code}]
            messages.append({
                "role": "function",
                "name": function_name,
                "content": function_response
            })
    
    # Only append if response_message.content is not None
    if response_message.content is not None:
        messages.append({"role": "assistant", "content": response_message.content})

    
    # Create a new response with the function results included
    model_response_with_function_call = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=1,
        max_tokens=512,
        messages=messages
    )
    
    return model_response_with_function_call.choices[0].message.content  # Access content directly


def get_current_date(country_name):
    """
    Get the current date for a given country.

    :param country_name: The name of the country, e.g., Turkey.
    :return: JSON string containing date information.
    """

    api_info['date_api']['parameters']['timeZone'] = country_name
    with open('api_info.json', 'w') as f:
        json.dump(api_info, f, indent=4)

    date_response = requests.get(api_info['date_api']['url'], params=api_info['date_api']['parameters'])
    if date_response.status_code == 200:
         date_data = date_response.json()
         date_message = f"Date API Response:\nYear: {date_data['year']}\nMonth: {date_data['month']}\nDay: {date_data['day']}\nHour: {date_data['hour']}\nMinute: {date_data['minute']}\nSeconds: {date_data['seconds']}"
         return date_message

def get_top_news(country_code):
    """
    Get the top news for a given country.

    :param country_code: The country code, e.g., 'tr' for Turkey, 'us' for United States.
    :return: JSON string containing news information.
    """
    
    api_info['news_api']['parameters']['country'] = country_code
    with open('api_info.json', 'w') as f:
        json.dump(api_info, f, indent=4)

    news_response = requests.get(api_info['news_api']['url'], params=api_info['news_api']['parameters'])
    if news_response.status_code == 200:
         news_data_list = news_response.json()
         news_message = "News API Response:\n"
         for news_data in news_data_list['articles']:
              news_message += f"Source: {news_data['source']['name']}\nTitle: {news_data['title']}\nPublished at: {news_data['publishedAt']}\nAuthor: {news_data['author']}\nURL: {news_data['url']}\n\n"
    return news_message

functions = [
    {
        "name": "get_current_date",
        "description": "Get the current date for a given country",
        "parameters": {
            "type": "object",
            "properties": {
                "country_name": {
                    "type": "string",
                    "description": "The name of the country, e.g., Turkey"
                }
            },
            "required": ["country_name"]
        }
    },
    {
        "name": "get_top_news",
        "description": "Get the top news for a given country",
        "parameters": {
            "type": "object",
            "properties": {
                "country_code": {
                    "type": "string",
                    "description": "The country code, e.g., 'tr' for Turkey, 'us' for United States"
                }
            },
            "required": ["country_code"]
        }
    }
]

print(openai_response())
