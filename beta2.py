import os, time, stat
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

to_gbs = lambda b: b / 1024**3

def walk_size(root):
    total = 0
    errors = 0
    dq = deque([root])
    while dq:
        path = dq.popleft()
        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        st = entry.stat(follow_symlinks=False)
                    except (OSError, OverflowError):
                        errors +=1
                        continue
                    if stat.S_ISDIR(st.st_mode):
                        dq.append(entry.path)
                    else:
                        total += st.st_size
        except OSError:
            errors += 1
            continue
    print(f"number of errors: {errors}")
    return total

def scan_drives(drives, max_workers=12):
    results = {}
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures_mapped = {pool.submit(walk_size, d.mountpoint): d.mountpoint for d in drives}
        for future in as_completed(futures_mapped):
            mount = futures_mapped[future]
            try:
                size_b = future.result()
                results[mount] = to_gbs(size_b)
            except Exception as e:
                results[mount] = f"error: {e}"
    elapsed = time.time() - start_time
    return results, elapsed

if __name__ == "__main__":
    import psutil
    drives = psutil.disk_partitions(all=True)
    print(drives[4])
    testing = [drives[4]]
    results, secs = scan_drives(drives) #change parameter to drives after testing
    print(results)
    print(f"total time taken: {secs / 60:.2f}")