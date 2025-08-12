import os, csv, datetime, win32wnet, win32com.client as win32, win32file, win32con



class csv_handler:
    """
    handles creating the csv file and outputting to it

    Args:
        drive_info (dictionary): values are strings which are paths to all root drive locations on pc and the keys are sums of all files on those drives

    Returns:
        outputs a .csv file with all information printed to it.
    """
    def __init__(self, drive_info, input_data):
        self.input = drive_info.results
        self.output = [["Drive", "Size", '']]
        self.input_data = input_data
        current_dir = os.getcwd()
        current_date = datetime.date.today()
        self.report_csv = os.path.join(current_dir, f"Report - {current_date}.csv")
        self.convert_dict()
        self.write_info()

    """
    function converts dictionary into a list format that is easy to output to .csv

    Args:
        None
    
    Returns:
        appends all information from the "input" dictionary into the "output" list
    """
    def convert_dict(self):
        for entry in self.input:
            if self.input_data.auto_scan is True:
                dtype = win32file.GetDriveType(entry)
                if dtype == win32con.DRIVE_REMOTE:
                    net_drive = entry.rstrip("\\")
                    self.output.append([win32wnet.WNetGetConnection(net_drive), f"{self.input[entry]:.2f}"])
            else:
                self.output.append([entry, f"{self.input[entry]:.2f}"])

    """
    
    """
    def write_info(self):
        with open(self.report_csv, 'a', newline='', encoding='utf-8') as csvfile:
            csv.writer(csvfile).writerows(self.output)