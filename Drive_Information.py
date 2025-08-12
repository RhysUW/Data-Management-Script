import os, time, stat, threading, psutil
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor


#function to convert bytes to gigbytes
to_gbs = lambda b: b / 1024**3

class drive_information: 
    def __init__(self, input_data):
        #drives will contain all the volumes available to the user
        self.input_data = input_data
        drives = psutil.disk_partitions(all=True)
        if(input_data.auto_scan):
            self.results, self.secs, self.errors = self.auto_scan_drives(drives)
        else:
            self.results, self.secs, self.errors = self.manual_scan_drives(input_data.drives) 
        
    r"""
        function adds all root drives (C:\\, G:\\, etc) to the queue of folders to be searched

        Args:
            volumes(list of lists): contains all the drives on the pc as a result of psuutil.disk_partitions() call
            q (queue): queue of tuples that contains the root drive (always) and a path to a specific folder in that root drive

        returns:
            populates the queue with all the root drives
    """
    def initialize_queue(self, volumes, q):
        if self.input_data.auto_scan is True:
            for drive in volumes:
                q.put((drive.device, drive.device))
        else:
            for drive in volumes:
                q.put((drive, drive))

    """
        function is responsible for extracting the size of every folder in each drive and summing them, adding the sum to the results dicitonary

        Args:
            q (queue): queue of tuples that contains the root drive (always) and a path to a specific folder in that root drive
            lock(Lock): lock for the threads to ensure mutual exclusion
            results(dictionary): root_drive_path: total # of bytes allocated in drive   

        Returns: 
            function increments the results[key] entry by the sum of all files in a given folder
    """
    def walk_size(self, queue, lock, results, errors):
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
                errors.append([path])
            finally:
                queue.task_done()
                
    """
    function initializes the working queue and the results, is utilized when the option to automatically detect and scan drives is chosen

    Args:
        drives (psutil disk partition list): list of information on all drives the user has access to.
        max_workers (int): maximum number of threads the program will create.

    returns:
        results (dictionary): each entry is a drive user has acess to and its associated value is the sum of all files in that drive, in GB's
        elapsed (float): total time in seconds the algorithm has been running
    """
    def auto_scan_drives(self, drives, max_workers=64):
        #queue of tuples where the tuple contains the root drive(G:\\, C:\\, etc) and the folder in that root to be searched
        q = Queue()
        #lock to ensure mutual exclusion
        lock = threading.Lock()
        #creates an entry for every drive the user has access too initially all are 0
        results = {d.device: 0 for d in drives}
        errors = []
        start_time = time.time()
        self.initialize_queue(drives, q)
        #creating 64 threads to run the walk_size function
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            for _ in range(max_workers):
                pool.submit(self.walk_size, q, lock, results, errors)
        elapsed = time.time() - start_time

        #converting bytes to GB's for output:
        for entry in results:
            results[entry] = to_gbs(results[entry])

        return results, elapsed, errors
    
    """
    Function is the same as auto_scan_drives however a few changed variables and function calls as this function uses a preset list of drives to scan over in the 
    config.json file

    Args:
        drives(list): contains all drives in the entire LSB branch, mainted in the config.json
        max_workers(int): defines the maximum amount of threads the program can create

    Return:
        results (dictionary): each entry is a drive user has acess to and its associated value is the sum of all files in that drive, in GB's
        elapsed (float): total time in seconds the algorithm has been running
    """
    def manual_scan_drives(self, drives, max_workers=64):
        #queue of tuples where the tuple contains the root drive(G:\\, C:\\, etc) and the folder in that root to be searched
        q = Queue()
        #lock to ensure mutual exclusion
        lock = threading.Lock()
        #creates an entry for every drive the user has access too initially all are 0
        results = {d: 0 for d in drives}
        errors = []
        start_time = time.time()
        self.initialize_queue(drives, q)
        #creating 64 threads to run the walk_size function
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            for _ in range(max_workers):
                pool.submit(self.walk_size, q, lock, results, errors)
        elapsed = time.time() - start_time

        #converting bytes to GB's for output:
        for entry in results:
            results[entry] = to_gbs(results[entry])

        return results, elapsed, errors 
