import os, time, stat, threading
from collections import deque
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed

#function to convert bytes to gigbytes
to_gbs = lambda b: b / 1024**3

r"""
    function adds all root drives (C:\\, G:\\, etc) to the queue of folders to be searched

    Args:
        volumes(list of lists): contains all the drives on the pc as a result of psuutil.disk_partitions() call
        q (queue): queue of tuples that contains the root drive (always) and a path to a specific folder in that root drive

    returns:
        populates the queue with all the root drives
"""
def initialize_queue(volumes, q):
    for drive in volumes:
        q.put((drive.device, drive.device))

"""
    function is responsible for extracting the size of every folder in each drive and summing them, adding the sum to the results dicitonary

    Args:
        q (queue): queue of tuples that contains the root drive (always) and a path to a specific folder in that root drive
        lock(Lock): lock for the threads to ensure mutual exclusion
        results(dictionary): root_drive_path: total # of bytes allocated in drive   
"""
def walk_size(queue, lock, results):
    errors = 0
    while True:
        try:
            #path is the path to the folder to scan
            #key is the root drive to add the sum of the files in 'path' to
            path, key = queue.get(timeout=1)
        #exit condition if the queue is empty terminate the thread
        except Empty:
            return
        try:
            with os.scandir(path) as it:
                for item in it:
                    try:
                        #a list containing information on the file
                        #the st_size attribute will contain the # of bytes the file takes up
                        st = item.stat(follow_symlinks=False)
                    except (OSError, OverflowError):
                        errors += 1
                    #if the object is a directory add it back to the queue to be scanned later, keep the same key, as the key is always the root drive to add the sum too
                    if stat.S_ISDIR(st.st_mode):
                        queue.put((item.path, key))
                    else:
                        #if its not a directory it is a file that needs to be added to the total sum, lock is envoked to ensure mutual exclusion
                        with lock:
                            results[key] += st.st_size
        except (OSError, OverflowError):
            errors += 1
        finally:
            queue.task_done()
            
"""
function initializes the working queue and the results 
"""
def scan_drives(drives, max_workers=64):
    #queue of tuples where the tuple contains the root drive(G:\\, C:\\, etc) and the folder in that root to be searched
    q = Queue()
    #lock to ensure mutual exclusion
    lock = threading.Lock()
    #creates an entry for every drive the user has access too initially all are 0
    results = {d.device: 0 for d in drives}
    start_time = time.time()
    initialize_queue(drives, q)
    #creating 64 threads to run the walk_size function
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
    #drives will contain all the volumes available to the user
    drives = psutil.disk_partitions(all=True)
    results, secs = scan_drives(drives) 
    print(results)
    print(f"total time taken: {secs / 60:.2f}")