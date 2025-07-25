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
    file_size = 0
    print(f"this is drive {dir_path}")
    try:
        with os.scandir(dir_path) as drive:
            for entry in drive:
                if entry.is_file():
                    file_info = os.stat(entry)
                    file_size += file_info.st_size
                if entry.is_dir():
                    file_size = allocated_size_of_directory(entry.path)
                dir_sum += file_size
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
    results[dir_path] = to_lib(allocated_size_of_directory(dir_path))

#list of drives the user has access to
drives = psutil.disk_partitions(all=True)
#list to keep track of all threads created
threads = []

results = {}

#creating a thread for every drive the user has access to
for drive in drives:
    drive_type = win32file.GetDriveType(drive.device)
    #diferentiate between network drive and local drives as they need to call seperate methods to get the path name
    if drive_type == win32con.DRIVE_REMOTE:
        t = threading.Thread(target=worker, args=(win32wnet.WNetGetUniversalName(drive.device), results))
        threads.append(t)
    else:
        t = threading.Thread(target=worker, args=(win32file.GetFullPathName(drive.device), results))
        threads.append(t)


for t in threads:
    t.start()

for t in threads:
    t.join()

print(results)