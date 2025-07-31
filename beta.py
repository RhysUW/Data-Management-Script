import os, threading, psutil, win32file, win32wnet, win32con, time

#functions to convert bytes to terabytes and gigabytes
to_lib = lambda b: b / 1024**4
to_gbs = lambda b: b / 1024**3

"""
This function is summing the size of all files in a given directory

Args:
    dir_path (undecided): a path to a given directory to parse
    link(Thread): thread sent to complete this task

Results:
    stores the sum of the file size's in the results list 
"""

def allocated_size_of_directory(dir_path):
    dir_sum = 0
    try:
        with os.scandir(dir_path) as drive:
                for entry in drive:
                        if entry.is_file():
                            dir_sum += entry.stat(follow_symlinks=False).st_size
                        elif entry.is_dir():
                            dir_sum += allocated_size_of_directory(entry.path)

    except OSError:
        pass
    return dir_sum

"""
Function is all the work a thread will do over its lifespan

Args:
    dir_path (undecided): path to directory the thread will work on
    link (thread): thread to be controlled

results:
    undecided
"""
def worker(dir_path, results):
    results[dir_path] = to_gbs(allocated_size_of_directory(dir_path))

def create_threads(drives):
    #for drive in drives:
        drive_type = win32file.GetDriveType(drives[4].device)
        #diferentiate between network drive and local drives as they need to call seperate methods to get the path name
        if drive_type == win32con.DRIVE_REMOTE:
            t = threading.Thread(target=worker, args=(win32wnet.WNetGetUniversalName(drives[4].device), results))
            threads.append(t)
        else:
            t = threading.Thread(target=worker, args=(win32file.GetFullPathName(drives[4].device), results))
            threads.append(t)


#list of drives the user has access to
drives = psutil.disk_partitions(all=True)
start_time = time.time()
#list to keep track of all threads created
threads = []

results = {}

test = psutil.disk_partitions()
print(drives[4])

#creating a thread for every drive the user has access to
create_threads(drives)

for t in threads:
    t.start()

for t in threads:
    t.join()

end_time = time.time()
time_elapsed = end_time - start_time
print(results)
print(f"Total execution time: {time_elapsed:.2f} seconds")
