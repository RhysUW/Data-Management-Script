import os, time, stat, threading
from collections import deque
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed

to_gbs = lambda b: b / 1024**3

def initialize_queue(volumes, q):
    for drive in volumes:
        q.put((drive.device, drive.device))


def walk_size(queue, lock, results):
    errors = 0
    while True:
        try:
            path, key = queue.get(timeout=1)
        except Empty:
            return
        try:
            with os.scandir(path) as it:
                for item in it:
                    try:
                        st = item.stat(follow_symlinks=False)
                    except (OSError, OverflowError):
                        errors += 1
                    if stat.S_ISDIR(st.st_mode):
                        queue.put((item.path, key))
                    else:
                        with lock:
                            results[key] += st.st_size
        except (OSError, OverflowError):
            errors += 1
        finally:
            queue.task_done()
            

def scan_drives(drives, max_workers=64):
    q = Queue()
    lock = threading.Lock()
    results = {d.device: 0 for d in drives}
    start_time = time.time()
    initialize_queue(drives, q)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for _ in range(max_workers):
            pool.submit(walk_size, q, lock, results)
    elapsed = time.time() - start_time

    #converting bytes to GB's for output:
    for entry in results:
        results[entry] = to_gbs(results[entry])

    return results, elapsed

if __name__ == "__main__":
    import psutil
    drives = psutil.disk_partitions(all=True)
    print(drives[4])
    testing = [drives[4]]
    results, secs = scan_drives(drives) #change parameter to drives after testing
    print(results)
    print(f"total time taken: {secs / 60:.2f}")