from labjackcontroller.labtools import LabjackReader

device_type = "T7"
connection_type = "ETHERNET"
duration = 180
channels = ["AIN0", "AIN1", "AIN2", "AIN3"]
voltages = [10.0, 10.0, 10.0, 10.0]


# Instantiate a LabjackReader
my_lj = LabjackReader(device_type, connection=connection_type)

print(my_lj)

freq, packet_size = 7600.0, 16 #my_lj.find_max_freq(channels, voltages)

print(freq, packet_size)

data_proc = my_lj.collect_data(channels, voltages, duration, freq, resolution=0, sample_rate=packet_size, verbose=True)

#print(my_lj._reshape_data(0, 10))
print(my_lj.get_dataframe())
