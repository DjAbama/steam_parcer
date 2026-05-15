import requests
import time
import asyncio
import aiohttp
import json
from my_libs.generators import generator, iterator, counter
from my_libs.memoization import memoizetion
from my_libs.queue import enqueue, dequeue
from my_libs.event_emmiter import subscribe, unsubscribe, event_emmiter



async def get_games_list(api_key, games_per_request, session):
        last_id = 0
        delay = generator(0, 1)
        request_counter = counter(1)

        while True:
            url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
            current_request = next(request_counter)
            async with session.get(url, params={"key": api_key, "max_results": games_per_request, "last_appid": last_id}) as req:
                if req.status != 200:
                    print("Error:", req.status)
                    return 
                reques_data = await req.json()
                games_list = reques_data.get("response", {}).get("apps", [])
                last_id = reques_data.get("response", {}).get("last_appid")

                if not games_list:
                    break

                yield games_list

                if not last_id:
                    break

@memoizetion(eviction=3600.0, limit=1000)
async def get_game_info(appid, api_key, session):
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

async def discount_filter(target_discount, appid, api_key, request_limit, session):
        async with request_limit:

            await asyncio.sleep(1.5)
            
            info = await get_game_info(appid, api_key, session)
            if info and info.get("discount", 0) >= target_discount:
                await event_emmiter("discount_found", info)
                return info
            else:
                return None

async def create_discounts_list(discount, list_generator, api_key, session):
        games_list = await anext(list_generator)
        request_limit = asyncio.Semaphore(1)    

        tasks = [
            discount_filter(discount, game.get('appid'), api_key, request_limit, session)
            for game in games_list
            
        ]

        result = await asyncio.gather(*tasks)

        reuslt_without_none = []
        
        for item in result:
            if item is not None:
                reuslt_without_none.append(item)

        return reuslt_without_none

@memoizetion(eviction='LRU', limit=1000)
async def find_id(name, api_key, session):
        url = "https://store.steampowered.com/api/storesearch/"
        async with session.get(url, params={"term": name, "key": api_key, "cc": "ua"}) as req:
            if req.status != 200:
                print("Error:", req.status)
                return None
            data = await req.json()
            game_id = data.get("items", [])
            if len(game_id) > 0:
                return game_id[0].get("id")
            else:
                return None 

async def scan_user_games(discount, name_list, api_key, request_limit, session):
    tasks = [
        find_id(name, api_key, session)
        for name in name_list      
    ]

    id_list = await asyncio.gather(*tasks)

    id_list_wothout_none = []
    for item in id_list:
        if item is not None:
            id_list_wothout_none.append(item)


    tasks = [
        discount_filter(discount, game_id, api_key, request_limit, session)
        for game_id in id_list_wothout_none
    ]

    result = await asyncio.gather(*tasks)

    games_list = []
    for item in result:
        if item is not None:
            games_list.append(item) 

    return games_list 

async def scan_wishlist_games(discount, user_id, api_key, request_limit, session):
    url = "https://api.steampowered.com/IWishlistService/GetWishlist/v1/"
    async with session.get(url, params={"key": api_key, "steamid": user_id}) as req:
        if req.status != 200:
            print("Error:", req.status)
            return None
        data = await req.json()

        items = data.get("response", {}).get("items", [])
        games_list = []

        for item in items:
            game_id = item.get("appid")
            games_list.append(game_id)

    tasks = [
        discount_filter(discount, game_id, api_key, request_limit, session)
        for game_id in games_list
    ]

    result = await asyncio.gather(*tasks)
    
    games_list = []
    for item in result:
        if item is not None:
            games_list.append(item) 

    return games_list
        

    
         