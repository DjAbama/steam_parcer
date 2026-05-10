import time


def memoizetion(eviction, limit):
    def decorator(func):

        cache = {}

        def LFU_find(obj):
            least_used = None
            for item, data in obj.items():
                if least_used is None or data["uses"] < obj[least_used]["uses"]:
                    least_used = item
            return least_used

        def LRU_find(obj):
            return next(iter(obj))

        def Time_find(obj, seconds):
            timeout = None
            for item, data in obj.items():
                if time.time() - data["time"] > seconds:
                    if timeout is None or data["time"] < obj[timeout]["time"]:
                        timeout = item
            return timeout

        
        async def wrap(*args):

            
            cache_key = tuple(arg for arg in args if isinstance(arg, (int, str, float)))

           
            if cache_key in cache:
                cache[cache_key]["uses"] += 1
                cache[cache_key]["time"] = time.time()
                return cache[cache_key]["value"]

            if len(cache) >= limit:

                match eviction:
                    case 'LFU':
                        cache.pop(LFU_find(cache))
                    case 'LRU':
                        cache.pop(LRU_find(cache))

                if type(eviction) == float:
                    if Time_find(cache, eviction) is None:
                        cache.pop(LRU_find(cache))
                    else:
                        cache.pop(Time_find(cache, eviction))

                if callable(eviction):
                    cache.pop(eviction(cache))

            result = await func(*args)
            
            
            cache[cache_key] = {
                "value": result,
                "uses": 0,
                "time": time.time()
            }

            return result

        return wrap
    return decorator