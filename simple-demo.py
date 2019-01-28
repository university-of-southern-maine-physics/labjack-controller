from labjackcontroller.labtools import LabjackReader

device_type = "T7"
connection_type = "ETHERNET"
duration = 100
channels = ["AIN0", "AIN1"]


# Instantiate a LabjackReader
my_lj = LabjackReader(device_type, connection=connection_type)

freq, packet_size = my_lj.find_max_freq(channels, [10.0, 10.0])

print(freq, packet_size)

data_proc = my_lj.collect_data(channels, [10.0, 10.0], duration, freq, resolution=0, sample_rate=packet_size, verbose=True)

print(my_lj._reshape_data(0, 10))