import Drive_Information as di
import Csv_Handler as ch
from input_handler import Input_Handler as ih

input_data = ih()
drive_sums = di.drive_information(input_data)
ch.csv_handler(drive_sums, input_data)


print(f"from controller: {drive_sums.results}")
print(f"from controller: {drive_sums.secs / 60}")