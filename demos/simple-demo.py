from labjackcontroller.labtools import LabjackReader

duration = 10  # seconds
frequency = 100  # Hz
channels = ["AIN0"]
voltages = [10.0]


# Instantiate a LabjackReader
with LabjackReader("T7") as my_lj:
    my_lj.collect_data(channels, voltages, duration, frequency)

    # Get the data we collected.
    print(my_lj.to_dataframe())
