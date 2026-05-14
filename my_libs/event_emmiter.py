import asyncio

subs = {}

def subscribe(event, func):
    if event not in subs:
        subs[event] = []
    subs[event].append(func)

def unsubscribe(event, func):
    if func in subs[event]:
        subs[event].remove(func)

async def event_emmiter(event):
    if event in subs:
        for func in subs[event]:
            await func()