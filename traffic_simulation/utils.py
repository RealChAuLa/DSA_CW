# utils.py
import time

def validate_int(text):
    try:
        v = int(text)
        return True, v
    except:
        return False, None

def time_function(func, *args, **kwargs):
    t0 = time.time()
    res = func(*args, **kwargs)
    t1 = time.time()
    return res, (t1 - t0)
