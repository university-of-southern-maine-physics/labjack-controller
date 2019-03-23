from labjackcontroller.labtools import LabjackReader

device_type = "T7"
duration = 30
connection_type = "USB"
channels = ["AIN0", "AIN1", "AIN2", "AIN3"]
voltages = [10.0, 10.0, 10.0, 10.0]


# Instantiate a LabjackReader
my_lj = LabjackReader(device_type, connection_type=connection_type)

print(my_lj)

freq, scans_per_read = 1000, 500 #my_lj.find_max_freq(channels, voltages, num_seconds=10)

print(freq, scans_per_read)

data_proc = my_lj.collect_data(channels, voltages, duration, freq,
                               resolution=1,
                               scans_per_read=scans_per_read,
                               verbose=True)

print(my_lj.to_dataframe(mode="range", start=400, end=500))
