import os
import psutil, win32api, win32file, win32wnet, win32con, math, pathlib

"""
Script Prints all the drives the current PC has access too and its current storage capacity / fill
"""

#list of all drives the user has access to
partitions = psutil.disk_partitions(all=True)

#functions to convert bytes to terabytes and gigabytes
to_lib = lambda b: b / 1024**4
to_gbs = lambda b: b / 1024**3
for p in partitions:
    drive = psutil.disk_usage(p.device) 
    dtype = win32file.GetDriveType(p.device)
    if dtype == win32con.DRIVE_REMOTE:
        print(f"Drive: {win32wnet.WNetGetUniversalName(p.device)}")
        if(to_lib(drive.total) > 1):
            print(f"Total: {to_lib(drive.total):.1f}TB's")
            print(f"Free: {to_lib(drive.free):.1f}TB's")
        else:
            print(f"Total: {to_gbs(drive.total):.1f}GB's")
            print(f"Free: {to_gbs(drive.free):.1f}GB's")
        print()
    else:
        print(f"Drive: {win32file.GetFullPathName(p.device)}")
        if(to_lib(drive.total) > 1):
            print(f"Total: {to_lib(drive.total):.1f}TB's")
            print(f"Free: {to_lib(drive.free):.1f}TB's")
        else:
            print(f"Total: {to_gbs(drive.total):.1f}GB's")
            print(f"Free: {to_gbs(drive.free):.1f}GB's")
        print()

print(win32wnet.WNetGetUniversalName(r"G:\\"))
print(win32wnet.WNetGetUniversalName(r"G:\\"))