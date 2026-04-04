import time
import random

def generator(a, b):
    while(True):
        yield random.randint(a ,b)



def iterator(gen, seconds):
    counter = gen
    start = time.time()
    while(time.time() - start < seconds):
        print(next(counter))
        time.sleep(0.5)

iterator(generator(1,100), 6)
    


