import time
import random

def generator(a, b):
    while(True):
        yield random.randint(a ,b)

def counter(start_number):
    while(True):
        yield start_number
        start_number += 1



def iterator(gen, seconds):
    start = time.time()
    while(time.time() - start < seconds):
        print(next(gen))
        time.sleep(0.5)


    


