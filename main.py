import asyncio

from backend.main import process_user_games, scan_discounts

async def start_app(): 
    key = input("Steam Key: ")
    mode = input("1 - Enter games, 2 - Scan for discounts: ")

    if mode == "1":
        names = input("Names: ").split(",")
        results = process_user_games([n.strip() for n in names], key)
    else:
        discount = int(input("Target discount: "))
        results = scan_discounts(key, discount)

    print("Results:")

    async for game in results:
        print(f"{game['name']}: {game['current_price']} (-{game['discount']}%)")

   
asyncio.run(start_app())