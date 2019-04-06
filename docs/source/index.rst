.. labjack-controller documentation master file, created by
   sphinx-quickstart on Sat Apr  6 13:40:25 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

labjack-controller Documentation
==============================================

:Documentation: https://labjack-controller.readthedocs.io/
:Source Code: https://github.com/university-of-southern-maine-physics/labjack-controller
:Issue Tracker: https://github.com/university-of-southern-maine-physics/labjack-controller/issues
:Stack Overflow: https://stackoverflow.com/questions/tagged/labjack-controller

labjack-controller is a Python package that enables powerful interactions with `Labjack <https://labjack.com>`_ DAQs.
Significant benefits include:

- Automatic device configuration for the user's desired task.
- Automatic configuration correction if you initialized device parameters in
  an invalid fashion.
- Ability to use as a shared object between processes.


Getting started is as simple as

.. code-block:: python

    from labjackcontroller.labtools import LabjackReader

    duration = 10  # seconds
    frequency = 100  # Hz
    channels = ["AIN0"]
    voltages = [10.0]


    # Instantiate a LabjackReader
    with LabjackReader("T7") as my_lj:
        # Stream data
        my_lj.collect_data(channels, voltages, duration, frequency)

        # Get the data we collected.
        print(my_lj.to_dataframe())


.. toctree::
   :maxdepth: 2
   :glob:

   installation
   demos
   Module Documentation <modules>
