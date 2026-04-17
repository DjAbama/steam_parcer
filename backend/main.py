import requests
import time
import json
from my_libs.generators import generator, iterator, counter
from my_libs.memoization import memoizetion
from my_libs.queue import enqueue, dequeue

queue = {}

def get_games_list(api_key, games_per_request):
    last_id = 0
    delay = generator(1, 3)
    request_counter = counter(1)

    while True:
        url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
        current_request = next(request_counter)

        req = requests.get(url, params={"key": api_key, "max_results": games_per_request, "last_appid": last_id})

        if req.status_code != 200:
            print("Error:", req.status_code)
            return None

        games_list = req.json().get("response", {}).get("apps", [])
        last_id = req.json().get("response", {}).get("last_appid")

        print("current request:", current_request)

        for game in games_list:
            yield game



        time.sleep(next(delay))

@memoizetion(eviction='LRU', limit=1000)
def get_game_details(appid, api_key):
    url = "https://store.steampowered.com/api/appdetails"
    req = requests.get(url, params={"appids": appid, "key": api_key, "cc": "us"})
    if req.status_code == 200:
        data = req.json()
        game_info = data.get(str(appid), {}).get('data', {})
        if data.get(str(appid), {}).get("success"):
            return {
                "appid": appid,
                "name": game_info.get("name"),
                "regular_price": game_info.get("price_overview", {}).get("initial_formatted"),
                "current_price": game_info.get("price_overview", {}).get("final_formatted"),
                "discount": game_info.get("price_overview", {}).get("discount_percent", 0),               
            }

def find_game_id(name, api_key):

    url = "https://store.steampowered.com/api/storesearch/"

    req = requests.get(url, params={"term": name, "key": api_key, "cc": "ua"})

    if req.status_code == 200:
        data = req.json()
        if data.get("items"):
            return data["items"][0].get("id")
        else:
            return None
    else:
        return None

def create_queue(q, game_id, priority):
    enqueue(q, game_id, priority)
    return q

