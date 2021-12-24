import requests
from datetime import datetime, timedelta
from twilio.rest import Client
import os


#--------Functions-------#
def get_weekday():
    weekday= datetime.now().weekday()
    if weekday == 0:
        yesterday = str((datetime.now() - timedelta(3)).date())
        day_before_yesterday = str((datetime.now() - timedelta(4)).date())
    elif weekday == 1:
        yesterday = str((datetime.now() - timedelta(1)).date())
        day_before_yesterday = str((datetime.now() - timedelta(5)).date())
    elif weekday == 6:
        yesterday = str((datetime.now() - timedelta(2)).date())
        day_before_yesterday = str((datetime.now() - timedelta(3)).date())
    else:
        yesterday=str((datetime.now() - timedelta(1)).date())
        day_before_yesterday=str((datetime.now() - timedelta(2)).date())
    return [yesterday, day_before_yesterday]

def get_difference(data_yesterday, data_day_before_yesterday):
    close_y = float(data_yesterday['4. close'])
    close_d_b_y = float(data_day_before_yesterday['4. close'])
    difference = 100-(100/close_d_b_y*close_y)
    if difference >= 0:
        return f'TSLA: 🔺{round(difference,2)}%'
    elif difference < 0:
        return f'TSLA: 🔻{round((-1)*difference,2)}%'

#-------Get day-------#
yesterday = get_weekday()[0]
day_before_yesterday = get_weekday()[1]

#-------Twilio API-----#
account_sid = os.environ['account_sid']
auth_token = os.environ['auth_token']
twilio_number = os.environ['twilio_number']
MY_NUMBER = os.environ['MY_NUMBER']

#--------Stock API---------#
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API_KEY = os.environ['STOCK_API_KEY']
STOCK_ENDPOINT = os.environ['STOCK_ENDPOINT']
parameters_stock = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK,
    'outputsize':'compact',
    'apikey': STOCK_API_KEY
}

#--------News API---------#
NEWS_ENDPOINT = os.environ['NEWS_ENDPOINT']
NEWS_API_KEY = os.environ['NEWS_API_KEY']
parameters_news = {
    'apikey': NEWS_API_KEY,
    'q': COMPANY_NAME,
    'sortBy': 'popularity',
    'from': day_before_yesterday,
    'to': yesterday
}

#-------Get Stock API--------#
response = requests.get(STOCK_ENDPOINT,params=parameters_stock)
response.raise_for_status()

data_yesterday = response.json()['Time Series (Daily)'][yesterday]
data_day_before_yesterday = response.json()['Time Series (Daily)'][day_before_yesterday]

# print(data_yesterday)
# print(data_day_before_yesterday)
# print(get_difference(data_yesterday,data_day_before_yesterday))

#-------Get news API---------#
response2 = requests.get(NEWS_ENDPOINT, params=parameters_news)
response2.raise_for_status()

news_data = response2.json()['articles'][:3]

#--------Define textmessage in Twilio format-------#

message = f"{get_difference(data_yesterday,data_day_before_yesterday)}\n\n"
for article in news_data:
    message += f"{article['title']}\n{article['description']}\n\n"

#print(message)

#--------Generate Twilio client object-------#
client = Client(account_sid, auth_token)
message = client.messages \
    .create(
    body=message,
    from_=twilio_number,
    to=MY_NUMBER
)
print(message.status)