import requests
import time
import json
from my_libs.generators import generator, iterator, counter



def get_games_list(api_key):
    last_id = 0
    delay = generator(1, 3)
    request_counter = counter(1)

    while True:
        url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
        current_request = next(request_counter)

        req = requests.get(url, params={"key": api_key, "max_results": 10000, "last_appid": last_id})

        if req.status_code != 200:
            print("Error:", req.status_code)
            return None

        games_list = req.json().get("response", {}).get("apps", [])
        last_id = req.json().get("response", {}).get("last_appid")

        print("current request:", current_request)

        for game in games_list:
            yield game



        time.sleep(next(delay))

key = str(input("Steam api key:"))

iterator(get_games_list(key), 10000)
