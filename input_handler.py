import json

class Input_Handler:
    def __init__(self):
        with open('config.json', 'r') as f:
            self.data = json.load(f)

        self.auto_scan = self.data['scan_drives?']
        self.drives = self.data['drives']