from labjackcontroller.labtools import LabjackReader

duration = 10  # seconds
frequency = 100  # Hz
channels = ["AIN0"]
voltages = [10.0]


my_lj = LabjackReader("T7")

# We don't need to explicitly open a connection, collect_data does it for us,
# but it is good practice.
my_lj.open()

# Actually stream data
my_lj.collect_data(channels, voltages, duration, frequency)

# We do need to explicitly close the connection when we don't want it anymore.
my_lj.close()

# Get the data we collected.
print(my_lj.to_dataframe())
