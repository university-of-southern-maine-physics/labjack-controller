# labjack-controller

## An Easy Python Wrapper for LJM to Just Take Data Already

This is a package designed to make streaming data from [LabJack](https://labjack.com/) devices easy.

## Device Compatibility

+ T7 and T7 Pro
+ T4
+ Digit-series devices

## Requirements

+ Python 3
+ [LJM](https://labjack.com/support/software/installers/ljm)
+ [Python for LJM](https://labjack.com/support/software/installers/ljm)

All other requirements will be automatically aqquired by `pip`; see `setup.py` for a complete list of all requirements that will be automatically obtained.

## Sample Usage

```python
from labjackcontroller.labtools import LabjackReader

myLabjack = LabjackReader("T7", connection="ETHERNET")

duration = 60  # Seconds
scan_rate = 50000  # Hz
max_channel_voltages = [10.0, 10.0]  # Volts
channels = ["AIN0", "AIN1"]

# Collect data from the above channels for 60 seconds.
myLabjack.collect_data(channels, max_channel_voltages, duration, scan_rate)

# Get all data recorded as a 2D Numpy array
my_data = myLabjack.to_list()
```

## Contributors

+ [Ben Montgomery](https://github.com/Nyctanthous)
