from labjackcontroller.labtools import LabjackReader

duration = 10  # seconds
frequency = 100  # sampling frequency in Hz
channels = ["AIN0", "DIO1"]  # read Analog INput 0, Digital INput 1.

analog_voltages = [10.0]  # i.e. read input voltages from -10 to 10 volts


# Instantiate a LabjackReader
with LabjackReader("T7") as my_lj:
    my_lj.collect_data(channels, analog_voltages, duration, frequency)

    # Get the data we collected.
    print(my_lj.to_dataframe())
