# from ..scaffold-server.app.models import 

import base64
import os
import requests

from app import create_app
from app.extensions import redis_client

application = create_app()

APPLICATION_KEY = os.environ.get("SCHWAB_APPLICATION_KEY")
APPLICATION_SECRET = os.environ.get("SCHWAB_APPLICATION_SECRET")

if __name__ == '__main__':

    with application.app_context():

        call_back_url = "https://127.0.0.1"

        authUrl = f'https://api.schwabapi.com/v1/oauth/authorize?client_id={APPLICATION_KEY}&redirect_uri=https://127.0.0.1'
        print(f"Click to authenticate: {authUrl}")

        returnedLink = input("Paste the redirect URL here:")

        code = f"{returnedLink[returnedLink.index('code=')+5:returnedLink.index('%40')]}@"

        headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{APPLICATION_KEY}:{APPLICATION_SECRET}", "utf-8")).decode("utf-8")}', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': 'https://127.0.0.1'}
        response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
        tD = response.json()

        access_token = tD['access_token']
        refresh_token = tD['refresh_token']

        # print(access_token)
        # print(refresh_token)        

        redis_client.set("access_token", access_token)
        redis_client.set("refresh_token", refresh_token)
