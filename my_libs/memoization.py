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


        def wrap(*args):


            if args in cache:
                cache[args]["uses"] += 1
                cache[args]["time"] = time.time()
                return cache[args]["value"]


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

            result = func(*args)
            cache[args] = {
                "value": result,
                "uses": 0,
                "time": time.time()
            }

            return result

        return wrap
    return decorator


