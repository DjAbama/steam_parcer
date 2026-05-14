import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

from backend.main import get_games_list, create_discounts_list, scan_user_games, scan_wishlist_games

bot = Bot(token="8687983204:AAHAvMLw5G3bv4tyqfZH0JsnTfVB0ckhIlA")
dp = Dispatcher()

global_session = None
users_db = {} 

@dp.startup()
async def on_startup():
    global global_session
    global_session = aiohttp.ClientSession()

nav_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Find discounts")],
        [KeyboardButton(text="Search games"), KeyboardButton(text="Scan wishlist")]
    ],
    resize_keyboard=True
)

def get_pagination_keyboard(current_page):
    buttons = []
    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="<- Previous", callback_data="prev_page"))
    buttons.append(InlineKeyboardButton(text="Next ->", callback_data="next_page"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def format_results(results, page):
    if not results:
        return f"Page {page + 1}: Nothing found"
    text = "\n".join([f"🎮 {g['name']}: {g['current_price']} (-{g['discount']}%)" for g in results])
    return f"Page {page + 1}:\n{text}"

@dp.message(CommandStart())
async def start(message: Message):
    users_db[message.from_user.id] = {"state": "wait_key"}
    await message.answer("Steam Api Key:")

@dp.message(F.text == "Find discounts")
async def ask_discount(message: Message):
    users_db[message.from_user.id]["state"] = "wait_discount"
    await message.answer("Discount %:")

@dp.message(F.text == "Search games")
async def ask_games(message: Message):
    users_db[message.from_user.id]["state"] = "wait_search"
    await message.answer("Games (comma separated):")

@dp.message(F.text == "Scan wishlist")
async def ask_wishlist(message: Message):
    users_db[message.from_user.id]["state"] = "wait_wishlist"
    await message.answer("Steam ID:")

@dp.message()
async def process_all_text(message: Message):
    user_id = message.from_user.id
    
    if user_id not in users_db:
        return await message.answer("Enter /start")

    current_state = users_db[user_id].get("state")
    text = message.text.strip()
    api_key = users_db[user_id].get("api_key")

    if current_state == "wait_key":
        users_db[user_id]["api_key"] = text
        users_db[user_id]["state"] = None
        await message.answer("API key saved", reply_markup=nav_panel)

    elif current_state == "wait_discount":
        discount = int(text)
        generator = get_games_list(api_key, games_per_request=100, session=global_session)
        
        users_db[user_id]["discount"] = discount
        users_db[user_id]["gen"] = generator
        users_db[user_id]["page"] = 0
        
        wait_msg = await message.answer("Loading...")
        results = await create_discounts_list(discount, generator, api_key, global_session)
        
        users_db[user_id]["history"] = [results]
        users_db[user_id]["state"] = None
        
        await wait_msg.edit_text(format_results(results, 0), reply_markup=get_pagination_keyboard(0))

    elif current_state == "wait_search":
        names_list = [n.strip() for n in text.split(",") if n.strip()]
        await message.answer("Loading...")
        
        results = await scan_user_games(50, names_list, api_key, asyncio.Semaphore(10), global_session)
        
        if results:
            res_text = "\n".join([f"🎮 {g['name']}: {g['current_price']} (-{g['discount']}%)" for g in results])
            await message.answer(f"Results:\n{res_text}")
        else:
            await message.answer("Nothing found")
            
        users_db[user_id]["state"] = None

    elif current_state == "wait_wishlist":
        await message.answer("Loading...")
        
        results = await scan_wishlist_games(50, text, api_key, asyncio.Semaphore(10), global_session)
        
        if results:
            res_text = "\n".join([f"🎮 {g['name']}: {g['current_price']} (-{g['discount']}%)" for g in results[:15]])
            await message.answer(f"Results:\n{res_text}")
        else:
            await message.answer("Nothing found")
            
        users_db[user_id]["state"] = None

@dp.callback_query(F.data.in_(["prev_page", "next_page"]))
async def paginate_discounts(call: CallbackQuery):
    await call.answer()
    
    user_id = call.from_user.id
    data = users_db.get(user_id)
    
    if not data:
        return await call.message.answer("Enter /start")

    if call.data == "prev_page":
        data["page"] -= 1
        
    elif call.data == "next_page":
        data["page"] += 1
        if data["page"] >= len(data["history"]):
            await call.message.edit_text("Loading...")
            try:
                results = await create_discounts_list(data["discount"], data["gen"], data["api_key"], global_session)
                data["history"].append(results)
            except StopAsyncIteration:
                data["page"] -= 1
                return await call.message.answer("No more games in Steam")

    results = data["history"][data["page"]]
    await call.message.edit_text(format_results(results, data["page"]), reply_markup=get_pagination_keyboard(data["page"]))

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))