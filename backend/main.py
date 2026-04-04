import requests
import json



def get_games_list(api_key):
    url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"

    games_list = requests.get(url, params={"key": api_key})
    print("list recieved")
    return games_list.json()

key = str(input("Steam api key:"))

get_games_list(key)