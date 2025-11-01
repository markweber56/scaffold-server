import base64
import os
import requests
import time
import sys

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.extensions import redis_client
from app.models.prices import Price
from app import create_app
from datetime import datetime, timedelta


app_key = os.environ.get("SCHWAB_APPLICATION_KEY")
secret = os.environ.get("SCHWAB_APPLICATION_SECRET")

TOKEN_URL = 'https://api.schwabapi.com/v1/oauth/token'
MARKET_DATA_URL = 'https://api.schwabapi.com/marketdata/v1/'

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
tickers = ['A', 'AAPL', 'ABBV', 'ABNB', 'ABT', 'ACGL', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'AMZN']
args = f"symbols={','.join(tickers)}"

OUTPUT_FILE_PATH = "./data.txt"
application = create_app()
headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{app_key}:{secret}", "utf-8")).decode("utf-8")}', 'Content-Type': 'application/x-www-form-urlencoded'}


def milliseconds_to_cst(millis: int):
    t_utc = datetime.utcfromtimestamp(millis / 1000.0)
    t_cst = t_utc - timedelta(hours=5)
    return t_cst.strftime(DATE_FORMAT)


def milliseconds_to_utc(millis: int):
    return datetime.utcfromtimestamp(millis / 1000.0)


def create_log_message(msg: str, time_milliseconds: int):
    t_formatted = milliseconds_to_cst(time_milliseconds)
    return f"{t_formatted} - {msg}"


def get_refresh_token(refresh_token: str):
    data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    print(f'\n{datetime.utcnow()} ---------------------------------------------- Attempting to retrieve refresh token-----------------------------\n')

    response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
    status = response.status_code
    if status == 200:
        data = response.json()
        print(f"successfully retrieved token: {data['access_token']}")
        return data['access_token'], data['refresh_token']
    else:
        print(f"{status} - Failed to retrieve access token")
    return '', ''


def main():
    with application.app_context():

        db_session = db.session()

        refresh_token = redis_client.get('refresh_token').decode('utf-8')
        authorization_token = redis_client.get('access_token').decode('utf-8')

        REFRESH_TIME = datetime.utcnow() + timedelta(minutes=3)

        with open(OUTPUT_FILE_PATH, 'w') as output_file:
            while True:
                now = datetime.utcnow()

                if (REFRESH_TIME - now) < timedelta(minutes=2):
                    authorization_token, refresh_token = get_refresh_token(refresh_token)
                    redis_client.set('access_token', authorization_token)
                    REFRESH_TIME = now + timedelta(minutes=25)

                response = requests.get(f'{MARKET_DATA_URL}/quotes?{args}', headers={'Authorization': f'Bearer {authorization_token}'})

                status_code = response.status_code
                prices = []

                if status_code == 200:
                    data = response.json()
                    for ticker in tickers:
                        ticker_data = data[ticker]
                        t_ms = ticker_data['quote']['quoteTime']
                        last_price = ticker_data['quote']['lastPrice']
                        msg = f"{ticker}: ${last_price}"
                        print(create_log_message(msg, t_ms))
                        t_cst = milliseconds_to_cst(t_ms)
                        t_utc = milliseconds_to_utc(t_ms)
                        prices.append(Price(ticker=ticker, utc_time=t_utc, price=last_price))

                        print(f'{ticker},{t_cst},{last_price}', file=output_file)
                    print()
                    try:
                        db_session.add_all(prices)
                        db_session.commit()
                    except IntegrityError as x:
                        print(x._message)
                        sys.exit(1)

                else:
                    print(f"{status_code} - Failed to retrieve data")
                time.sleep(30)


if __name__ == '__main__':
    main()
