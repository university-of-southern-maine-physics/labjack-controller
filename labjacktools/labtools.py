from labjack import ljm
import numpy as np
from typing import List
from math import ceil
import time
from multiprocessing import RawArray, Value


class LabjackReader(object):
    """A class designed to represent an arbitrary LabJack device."""

    def __init__(self,
                 type: str,
                 connection="ANY",
                 identifier="ANY") -> None:
        """
        Initialize a LabJack object.

        Parameters
        ----------
        type : str
            A LabJack model, such as T7, U6, or U3.
        connection : {'ANY', 'USB', 'ETHERNET', or 'WIFI'}, optional
            Valid optionas are
            'ANY' for attempting any mode of connection
            'USB' for attempting connection over USB
            'ETHERNET' for attempting connection over Ethernet
            'WIFI' for attempting connection over WiFi
            Support for each of these modes is a function of the LabJack model
            you are connecting to. When 'ANY' is selected, the LabJack library
            generally defaults to the fastest avaliable connection.
        identifier : str, optional
            The user-designated name of the LabJack device.

        Returns
        -------
        None

        """
        # Also keep track of the input channels we're reading.
        self.input_channels = None

        # Declare a data storage handle
        self.data_arr = None

        # Also, specify the largest index that is populated.
        self.max_index = None

        self.connection_open = False

        self.type, self.connection, self.id = type, connection, identifier

    def get_max_data_index(self) -> int:
        """
        Return the largest index value that has been filled.

        Parameters
        ----------
        None

        Returns
        -------
        max_index: int
            The index of the latest value that has been recorded.

        """
        if self.max_index is not None and self.max_index.value:
            return self.max_index.value
        else:
            return -1

    def open_stream(self) -> None:
        """
        Open a streaming connection to the LabJack.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        if not self.connection_open:
            # Open our device.
            try:
                self.handle = ljm.openS(self.type, self.connection,
                                        self.id)
                self.connection_open = True
            except ljm.LJMError as ljm_e:
                print("Failed to open LabJack device:", ljm_e)
                exit(1)

            info = ljm.getHandleInfo(self.handle)
            print("Opened a LabJack with Device type: %i,\n"
                  "Connection type: %i, Serial number: %i,\n"
                  "IP address: %s, Port: %i, Max bytes per MB: %i"
                  % (info[0], info[1], info[2],
                     ljm.numberToIP(info[3]), info[4], info[5]))

    def close_stream(self) -> None:
        """
        Close a streaming connection to the LabJack.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        if self.connection_open:
            try:
                # Try to close the stream
                print("\nStop Stream")
                ljm.eStreamStop(self.handle)
                self.connection_open = False
            except ljm.LJMError as ljm_e:
                print("Labjack error closing the stream:", ljm_e)
            except Exception as e:
                print("Python error closing the stream:", e)

    def write_data_to_file(self, filename: str, mode='w') -> None:
        """
        Write a queue of datapoints to a file named filename.

        Parameters
        ----------
        filename : str
            A filename, such as "xyz.txt", that specifies this file.
        mode : {'r+', 'w', 'w+', or 'a'}, optional
            Valid options are
            'r+' for reading and writing, without file truncation
            'w' for writing
            'w+' for reading and writing, with file truncation
            'a' for append mode

        Returns
        -------
        None

        """
        if not len(self.data_arr):
            raise Exception("No data to write to file.")
        if mode not in ['r+', 'w', 'w+', 'a']:
            raise Exception("Invalid file write mode specified.")
        if not isinstance(filename, str) or not len(filename):
            raise Exception("Bad filename given.")

        with open(filename, mode) as f:
            # Reshape the data into rows, where every row is a moment in time
            # where all channels were sampled at once.
            curr_queue = np.array(self.data_arr) \
                            .reshape((ceil(len(self.data_arr)
                                           / (len(self.input_channels) + 1)),
                                     len(self.input_channels) + 1))

            # Write header.
            f.write(" ".join(self.input_channels) + ' time\n')

            # Write data.
            for voltages in curr_queue:
                f.write(" ".join([str(item) for item in voltages]) + '\n')

    def get_data(self, from_index=0, to_index=-1) -> List[List[float]]:
        """
        Return data in latest array.

        Parameters
        ----------
        from_index : int, optional
            Starting index in recorded data array. Does not check if the index
            provided is valid.
        to_index : int, optional
            Ending index in recorded data array. Does not check if the index
            provided is valid.

        Returns
        -------
        array_like: ndarray
            A 2D array in the shape (ceil(1d data len/ number of channels),
                                     number of channels)

        Notes
        -----
        If the internal data array has not been initialized yet, the return
        value of this function will be None.

        """
        if self.data_arr is not None:
            return np.frombuffer(self.data_arr[0:-1], dtype=np.float32) \
                    .reshape((ceil(len(self.data_arr) /
                                   (len(self.input_channels) + 1)),
                             len(self.input_channels) + 1))
        # Else...
        return None

    def collect_data(self,
                     inputs: List[str],
                     inputs_max_voltages: List[float],
                     seconds: float,
                     scan_rate: int,
                     scans_per_read=1,
                     stream_setting=0,
                     resolution=8) -> None:
        """
        Collect data from the LabJack device.

        Data collection will overwrite any data stored in this object's
        internal array.

        Parameters
        ----------
        inputs: sequence of strings
            Names of input channels on the LabJack device to read.
            Must correspond to the actual name on the device.
        inputs_max_voltages: sequence of real values
            Maximum voltages corresponding element-wise to the channels
            listed in inputs.
        seconds: float
            Duration of the data run in seconds. The run will last at least as
            long as this value, and will try to stop streaming when this time
            has been met.
        scan_rate: int
            Number of times per second (Hz) the device will get a datapoint for
            each of the channels specified.
        scans_per_read: int, optional
            Number of data points contained in a packet sent by the LabJack
            device.
        stream_setting: int, optional
            See official LabJack documentation.
        resolution: int, optional
            See official LabJack documentation.

        Returns
        -------
        None

        Examples
        --------
        Create a reader for a Labjack T7 and read off 60.5 seconds of data at
        50 kHz from channels AIN0, AIN1 which have a maximum voltage of 10V
        each:

        >>> reader = LabjackReader("T7")
        >>> reader.collect_data(["AIN0", "AIN1"], [10.0, 10.0], 60.5, 50000)
        None

        """
        # Open a connection.
        self.open_stream()

        # Declare the ports we want to read, EG. AIN0 & AIN1
        num_addrs = len(inputs)
        aScanList = ljm.namesToAddresses(num_addrs, inputs)[0]

        try:
            # When streaming, negative channels and ranges can be configured
            # for individual analog inputs, but the stream has only one
            # settling time and resolution.

            # Ensure triggered stream is disabled.
            ljm.eWriteName(self.handle, "STREAM_TRIGGER_INDEX", 0)

            # Enabling internally-clocked stream.
            ljm.eWriteName(self.handle, "STREAM_CLOCK_SOURCE", 0)

            # All negative channels are single-ended, AIN0 and AIN1 ranges are
            # +/-10 V, stream settling is 0 (default) and stream resolution
            # index is 0 (default).
            aNames = ["AIN_ALL_NEGATIVE_CH",
                      *[element + "_RANGE" for element in inputs],
                      "STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            aValues = [ljm.constants.GND, *inputs_max_voltages,
                       stream_setting, resolution]

            # Write the analog inputs' negative channels (when applicable),
            # ranges, stream settling time and stream resolution configuration.
            numFrames = len(aNames)
            print("Before Write")
            ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
            print("Completed write")

            # Configure and start stream
            scanRate = ljm.eStreamStart(self.handle, scans_per_read, num_addrs,
                                        aScanList, scan_rate)
            print("\nStream started with a scan rate of %0.0f Hz." % scan_rate)

            # Python 3.7 has time_ns, upgrade to this when Conda supports it.
            start = time.time()
            totScans = 0
            totSkip = 0  # Total skipped samples

            self.input_channels = inputs

            # Create a RawArray for multiple processes; this array
            # stores our data.
            size = int(seconds*scan_rate*(len(inputs) + 1))
            self.data_arr = RawArray('d', size)

            packet_num = 0
            self.max_index = Value('l', 0)
            step_size = len(inputs)
            while time.time() - start < seconds:
                # Read all rows of data off of the latest packet in the stream.
                ret = ljm.eStreamRead(self.handle)
                read_time = time.time() - start

                # We will manually calculate the times each entry occurs at.
                # The stream itself is timed by the same clock that runs
                # CORE_TIMER, and it is officially advised we use the stream
                # clocking instead.
                # See https://forums.labjack.com/index.php?showtopic=6992
                expected_time = (scans_per_read/scan_rate)*packet_num

                # The delta between the expected time and the arrival time is
                # the error + travel time
                travel_time = read_time - expected_time

                # Calculate times that the data occurred at. See the CORE_TIMER
                # comment.
                for i in range(0, len(ret[0]) - 1, step_size):
                    curr_time = scans_per_read / scan_rate\
                                * (packet_num + i / scans_per_read)
                    if self.max_index.value >= size - step_size:
                        break

                    # We get a giant 1D list back, so work with what we have.
                    for datapoint in ret[0][i:i + step_size]:
                        self.data_arr[self.max_index.value] = datapoint
                        self.max_index.value += 1

                    # Put in the time as well
                    self.data_arr[self.max_index.value] = curr_time
                    self.max_index.value += 1

                packet_num += 1
                aData = ret[0]
                scans = len(aData) / num_addrs
                totScans += scans

                # Count the skipped samples which are indicated by -9999 values
                # Missed samples occur after a device's stream buffer overflows
                # and are reported after auto-recover mode ends.
                curSkip = aData.count(-9999.0)
                totSkip += curSkip

                ainStr = ""
                for j in range(0, num_addrs):
                    ainStr += "%s = %0.5f, " % (inputs[j], aData[j])
                if curSkip:
                    print("Scans Skipped = %0.0f" % (curSkip/num_addrs))

            # We are done, record the actual ending time.
            end = time.time()

            tt = end - start
            print("\nTotal scans = %i\
                  \nTime taken = %f seconds\
                  \nLJM Scan Rate = %f scans/second\
                  \nTimed Scan Rate = %f scans/second\
                  \nTimed Sample Rate = %f samples/second\
                  \nSkipped scans = %0.0f"
                  % (totScans, tt, scanRate, (totScans / tt),
                     (totScans * num_addrs / tt), (totSkip / num_addrs)))
        except ljm.LJMError as ljm_e:
            print("Labjack error collecting data:", ljm_e)
        except Exception as e:
            print("Python error collecting data:", e)

        # Close the connection.
        self.close_stream()
