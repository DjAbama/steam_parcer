import time


def highest_priority(obj):
        if not obj: 
            return None 
        highest = None
        for key, data in obj.items():
            if highest is None or data["priority"] > obj[highest]["priority"]:
                highest = key
        return highest
    
def lowest_priority(obj):
    if not obj: 
        return None 
    lowest = None
    for key, data in obj.items():
        if lowest is None or data["priority"] < obj[lowest]["priority"]:
            lowest = key
    return lowest
    
def oldest(obj):
    if not obj: 
        return None 
    oldest_item = list(obj.keys())[0] 
    return oldest_item
    
def newest(obj):
    if not obj: 
        return None 
    newest_item = list(obj.keys())[-1]
    return newest_item

def enqueue(queue, item, priority):

    if item in queue:
        print(item, "is already in the queue")
        return
    else:
        queue[item] = {
            "priority": priority,
            "time": time.time()
        }
    return queue


def peek(queue, strategy):

    match strategy:
        case "highest":
            return highest_priority(queue)
        case "lowest":
            return lowest_priority(queue)
        case "oldest":
            return oldest(queue)
        case "newest":
            return newest(queue)
        

def dequeue(queue, strategy):

    item = peek(queue, strategy) 
        
    if item is not None:
        queue.pop(item) 
        return item     
    else:
        return None
