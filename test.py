import os
import threading, time

"""
print(os.listdrives())
print(os.listvolumes())
print(os.scandir(path='C:\\'))
print(os.listdir(path='H:\\'))
"""


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

with os.scandir("c:\\") as drive:
    for entry in drive:
        print(f"C:\\{entry}")
        if entry.is_dir():
            print(os.scandir(f"{entry.path}"))


