import Drive_Information as di
import Csv_Handler as ch

drive_sums = di.drive_information()
ch.csv_handler(drive_sums.results)


print(f"from controller: {drive_sums.results}")
print(f"from controller: {drive_sums.secs}")