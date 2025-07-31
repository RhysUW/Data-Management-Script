import os, win32file
import threading, time, psutil
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty

"""
print(os.listdrives())
print(os.listvolumes())
print(os.scandir(path='C:\\'))
print(os.listdir(path='H:\\'))
"""

to_lib = lambda b: b / 1024**4
to_gbs = lambda b: b / 1024**3

#trying threads

def calculation(link, value, delay):
    print(f"thread started execution for {link} with value {value}")
    time.sleep(delay)
    value *= 2
    time.sleep(delay)
    print(f"thread ending for {link} value is now {value}")
    return value

def worker(link, value, results, index):
    results[index] = calculation(link, value, delay=index)

links = [
    "Thread 1",
    "Thread 2",
    "Thread 3"
]

numbers = [
    2, 
    5,
    10
]

#creating the threads
threads = []
i = 0

results = [None] * len(links)
"""
for link in links:
    t = threading.Thread(target=worker, args=(link, numbers[i], results, i))
    threads.append(t)
    i += 1

#starting the threads
for t in threads:
    t.start()

for t in threads:
    t.join()

print(f"results: {results}")



with os.scandir(r"H:\Profile\Documents\Data Managment Application\test files") as drive:
    for entry in drive:
        print(f"C:\\{entry}")
        print(f"filesize: {win32file.GetFileSize(entry)}")
        if entry.is_dir():
            print(os.scandir(f"{entry.path}"))

"""
MAX_WORKERS = 3

#sum should be 73
collection1 = [[4, 10], 17, 25, 9, 8]

#sum should be 203
collection2 = [[1, 0], [100, 40, 5], 9, 48]

#sum should be 1845
collection3 = [[[3, 3], 6, 10], [8, 9, 10, 50, 70, 80], [100, 20, 44, 400], 900, 109, 23]

#sum should be 15
collection4 = [10, 5]

q = Queue()
q.put(("col1" ,collection1))
q.put(("col2" ,collection2))
q.put(("col3", collection3))
q.put(("col4", collection4))

results = {"col1": 0, "col2": 0, "col3": 0, "col4": 0}
lock = threading.Lock()

def scan_items(q, results, lock):
    while True:
        try:
            key, item = q.get(timeout=0.5)
        except Empty:
            return #worker is done
        if isinstance(item, list):
            for obj in item:
                q.put((key, obj))
        else:
            with lock:
                results[key] += item

        q.task_done()

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
    for _ in range(MAX_WORKERS):
        pool.submit(scan_items, q, results, lock)
    q.join()

for item in results:
    print(f"collection: {results[item]}")

