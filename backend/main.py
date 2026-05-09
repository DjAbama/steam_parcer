import requests
import time
import asyncio
import aiohttp
import json
from my_libs.generators import generator, iterator, counter
from my_libs.memoization import memoizetion
from my_libs.queue import enqueue, dequeue
from my_libs.async_arrays import Map_promise, Map_callback

'''
@memoizetion(eviction='LRU', limit=1000)
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
async def get_game_details(appid, api_key):
    url = "https://store.steampowered.com/api/appdetails"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"appids": appid, "key": api_key, "cc": "us"}) as req:
            if req.status == 200:
                data = await req.json()
                game_info = data.get(str(appid), {}).get('data', {})
                if data.get(str(appid), {}).get("success"):
                    return {
                "appid": appid,
                "name": game_info.get("name"),
                "regular_price": game_info.get("price_overview", {}).get("initial_formatted", "Free"),
                "current_price": game_info.get("price_overview", {}).get("final_formatted", "Free"),
                "discount": game_info.get("price_overview", {}).get("discount_percent", 0),               
            }

async def find_game_id(name, api_key):

    url = "https://store.steampowered.com/api/storesearch/"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"term": name, "key": api_key, "cc": "ua"}) as req:
            if req.status == 200:
                data = await req.json()
                if data.get("items"):
                    return data["items"][0].get("id")
                else:
                    return None
            else:
                return None


async def process_user_games(games_list, api_key):
    queue = {}

    id_list = await Map_promise(games_list, lambda name: find_game_id(name, api_key))

    for current_id in id_list:
        enqueue(queue, current_id, priority = 10)

    while queue:
        game_id = dequeue(queue, "highest")
        if not game_id: 
            break
        else: 
            info = await get_game_details(game_id, api_key)
            if info:
                yield info
        
    
async def scan_discounts(api_key, target_discount):

    scanned_list =get_games_list(api_key, games_per_request=100)

    for game in scanned_list:
        info = await get_game_details(str(game['appid']), api_key)

        if info and info.get("discount", 0) >= target_discount:
            yield info
'''

async def get_games_list(api_key, games_per_request):
    async with aiohttp.ClientSession() as session:
        last_id = 0
        delay = generator(1, 3)
        request_counter = counter(1)

        while True:
            await asyncio.sleep(next(delay))
            url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
            current_request = next(request_counter)
            async with session.get(url, params={"key": api_key, "max_results": games_per_request, "last_appid": last_id}) as req:
                if req.status != 200:
                    print("Error:", req.status)
                    return None
                reques_data = await req.json()
                games_list = reques_data.get("response", {}).get("apps", [])
                last_id = reques_data.get("response", {}).get("last_appid")

                if not games_list:
                    break

                yield games_list

                if not last_id:
                    break

async def get_game_info(appid, api_key):
    async with aiohttp.ClientSession() as session:
        url = "https://store.steampowered.com/api/appdetails"
        async with session.get(url, params={"appids": appid, "key": api_key, "cc": "us"}) as req:
            if req.status != 200:
                print("Error:", req.status)
                return None
            data = await req.json()
            game_info =  data.get(str(appid), {}).get("data", {})
            if data.get(str(appid), {}).get("success"):
                return {
                    "appid": appid,
                    "name": game_info.get("name"),
                    "regular_price": game_info.get("price_overview", {}).get("initial_formatted", "Free"),
                    "current_price": game_info.get("price_overview", {}).get("final_formatted", "Free"),
                    "discount": game_info.get("price_overview", {}).get("discount_percent", 0),    
                }

async def discount_filter(target_discount, appid, api_key, request_limit):
    async with aiohttp.ClientSession() as session:
        async with request_limit:

            await asyncio.sleep(1.5)
            
            info = await get_game_info(appid, api_key)
            if info.get("discount", 0) >= target_discount:
                return info
            else:
                return None

async def create_discounts_list(list_generator, api_key):
    games_list = await anext(list_generator)
    request_limit = asyncio.Semaphore(1)    

    tasks = [
        discount_filter(50, game.get('appid'), api_key, request_limit)
        for game in games_list
         
    ]

    results = await asyncio.gather(*tasks)

    reuslt_without_none = []
    
    for item in results:
        if item is not None:
            reuslt_without_none.append(item)

    




        