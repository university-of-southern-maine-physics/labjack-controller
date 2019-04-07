<h1 align="center">labjack-controller</h1>
<p style="text-align:center"><img src=https://labjack.com/sites/default/files/styles/slideshow/public/T7-Pro_engineering_sshow.jpg?itok=82O0k1DV/></p>

## An Easy Python Wrapper for LJM to Just Take Data Already

This is a package designed to make streaming data from [LabJack](https://labjack.com/) T-series devices easy.
## Device Compatibility

+ T7 and T7 Pro
+ T4

## Requirements

+ Python 3.5+
+ [LJM](https://labjack.com/support/software/installers/ljm)

All other requirements will be automatically acquired by `pip`; see `setup.py` for a complete list of all requirements that will be automatically obtained.

## Installation
[![Build Status](https://travis-ci.com/university-of-southern-maine-physics/labjack-controller.svg?branch=master)](https://travis-ci.com/university-of-southern-maine-physics/labjack-controller)
[![Documentation Status](https://readthedocs.org/projects/labjack-controller/badge/?version=latest)](https://labjack-controller.readthedocs.io/en/latest/?badge=latest)

You can install this package with `pip` through our `PyPi` package with the command
```bash
pip install labjackcontroller
```

Alternatively, you can install from this github repository with

```bash
git clone https://github.com/university-of-southern-maine-physics/labjack-controller.git
cd labjack-controller
pip install .
```

## Sample Usage

Multiple demonstrations of library functions are located in the `demos` folder, and you can [read the library documentation here.](https://labjack-controller.readthedocs.io/en/latest/index.html) However, getting started with full streaming is as easy as

```python
from labjackcontroller.labtools import LabjackReader

duration = 10  # seconds
frequency = 100  # Hz
channels = ["AIN0"]
voltages = [10.0]

# Instantiate a LabjackReader
with LabjackReader("T7") as my_lj:
    my_lj.collect_data(channels, voltages, duration, frequency)

    # Get all data recorded as a 2D Numpy array
    my_data = myLabjack.to_array()
```

## Contributors

+ [Ben Montgomery](https://github.com/Nyctanthous)

## Special Thanks

+ [Paul Nakroshis](https://github.com/paulnakroshis)
