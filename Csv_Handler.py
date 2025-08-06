import os, csv, datetime, win32wnet


class csv_handler:
    def __init__(self, drive_info):
        self.input = drive_info
        self.output = [["Drive", "Size", '']]
        current_dir = os.getcwd()
        current_date = datetime.date.today()
        self.report_csv = os.path.join(current_dir, f"Report - {current_date}.csv")
        self.convert_dict()
        self.write_info()

    def convert_dict(self):
        for entry in self.input:
            if entry != "C:\\":
                net_drive = entry.rstrip("\\")
                self.output.append([win32wnet.WNetGetConnection(net_drive), f"{self.input[entry]:.2f}"])

    def write_info(self):
        with open(self.report_csv, 'a', newline='', encoding='utf-8') as csvfile:
            csv.writer(csvfile).writerows(self.output)
