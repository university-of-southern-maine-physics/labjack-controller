from labjack import ljm
import numpy as np
from typing import List, Tuple, Union
from math import ceil
import time
from multiprocessing import RawArray


class LabjackReader(object):
    """A class designed to represent an arbitrary LabJack device."""

    def __init__(self,
                 device_type: str,
                 connection="ANY",
                 identifier="ANY") -> None:
        """
        Initialize a LabJack object.

        Parameters
        ----------
        type : str
            A LabJack model, such as T7 or T4
        connection : {'ANY', 'USB', 'ETHERNET', or 'WIFI'}, optional
            Valid options are
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
        # Handle if we were given bad args to initialize on.
        if not (isinstance(device_type, str)
                and isinstance(connection, str)
                and isinstance(identifier, str)):
            raise Exception("Invalid initialization parameters provided")

        self.type, self.connection = device_type, connection
        self.id = identifier

        # Keep track of the input channels we're reading.
        self.input_channels: List[str]
        self.input_channels = []

        # Declare a data storage handle
        self.data_arr: RawArray
        self.data_arr = None

        # Also, specify the largest index that is populated.
        self.max_index = 0

        # There will be an int handle for the LabJack device
        self.handle: int

        self.connection_open = False

    def get_connection_status(self):
        """
        Get the status of the connection to the LabJack

        Parameters
        ----------
        None

        Returns
        -------
        connection_open: bool
            True if the connection is open
            False if the connection is closed/does not exist

        """
        return self.connection_open

    def get_max_row(self) -> int:
        """
        Return the number of the last row that currently exists.

        Parameters
        ----------
        None

        Returns
        -------
        row: int
            The number of the last row recorded in the data array,
            or -1 on error
        """
        if not len(self.input_channels):
            raise Exception("No channels have been declared")
        max_index = self.get_max_data_index()

        if max_index < 1:
            return -1
        # Else...
        return int(max_index/(len(self.input_channels) + 1))

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
        if self.max_index is not None and self.max_index:
            return self.max_index
        else:
            return -1

    def save_data(self, filename: str, row_start: int, row_end: int, mode='w',
                  header=False) -> int:
        """
        Write recorded data points to a file named filename.

        Parameters
        ----------
        filename : str
            A filename, such as "xyz.txt", that specifies this file.
        row_start : The data point across all channels to start from.
                    0 is the very first one ever recorded.
        row_end : The last data point to include (eg. 10th).
                  If a value greater than the number of rows present
                  is given, only the rows present will be backed up
                  and no error will be thrown.
        mode : {'r+', 'w', 'w+', or 'a'}, optional
            Valid options are
            'r+' for reading and writing, without file truncation
            'w' for writing
            'w+' for reading and writing, with file truncation
            'a' for append mode
        header : A column header for each of the channels being read

        Returns
        -------
        num_rows : the number of rows actually written

        """
        if not len(self.input_channels):
            return -1
        if mode not in ['r+', 'w', 'w+', 'a']:
            raise Exception("Invalid file write mode specified.")
        if not isinstance(filename, str) or not len(filename):
            raise Exception("Bad filename given.")

        """
        with open(filename, mode) as f:
            # Write header.
            if header:
                f.write(" ".join(self.input_channels) + ' time\n')

            if self.data_arr is None or not len(self.data_arr):
                return 0

            # Reshape the data into rows, where every row is a moment in time
            # where all channels were sampled at once.
            curr_queue = self._reshape_data(row_start, row_end)

            if curr_queue is not None:
                # Write data.
                for signal in curr_queue:
                    f.write(" ".join([str(item) for item in signal]) + '\n')
                return len(curr_queue)
            return 0
        """
        if header:
            with open(filename, mode) as f:
                f.write(",".join(self.input_channels) + ',time\n')
        else:
            with open(filename, 'ab') as f:
                curr_data = self._reshape_data(row_start, row_end)
                if curr_data is not None:
                    np.savetxt(f, self._reshape_data(row_start, row_end), delimiter=',')
                    return len(curr_data)
        return 0

    def _reshape_data(self, from_row: int, to_row: int):
        """
        Get a range of rows from the recorded data

        Parameters
        ----------
        from_row: int
            The first row to include, inclusive.
        to_row: int
            The last row to include, non-inclusive.

        Returns
        -------
        array_like: ndarray
            A 2D array, starting at from_row, of data points, where
            every row is one data point across all channels.
        """
        if (self.data_arr is not None and self.get_max_data_index() != -1
           and from_row >= 0):
            row_width = len(self.input_channels) + 1
            max_index = min(self.get_max_data_index(), row_width*to_row)

            start_index = from_row*row_width

            return np.array(self.data_arr[start_index:max_index]) \
                .reshape((ceil((max_index - start_index) / row_width),
                         row_width))
        # Else...
        return None

    def get_data(self, num_rows) -> Union[List[List[float]], None]:
        """
        Return data in latest array.

        Parameters
        ----------
        num_rows : int, optional
            The number of rows to return. Number is relative to the end,
            or -1 for all rows.

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
        max_row = self.get_max_data_index()
        if max_row < 0:
            return None

        row_width = len(self.input_channels) + 1
        max_row = int(max_row / row_width)

        if num_rows < -1:
            raise Exception("Invalid number of rows provided")
        elif num_rows == -1:
            return self._reshape_data(0, max_row)
        else:
            return self._reshape_data(max_row - num_rows, max_row)

    def _open_connection(self):
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
            self.handle = ljm.openS(self.type, self.connection,
                                    self.id)
            self.connection_open = True

            info = ljm.getHandleInfo(self.handle)
            print("Opened a LabJack with Device type: %i,\n"
                  "Connection type: %i, Serial number: %i,\n"
                  "IP address: %s, Port: %i, Max bytes per MB: %i"
                  % (info[0], info[1], info[2],
                     ljm.numberToIP(info[3]), info[4], info[5]))

    def _close_stream(self) -> None:
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
            # Try to close the stream
            print("\nStop Stream")
            ljm.eStreamStop(self.handle)
            self.connection_open = False

    def _setup(self, inputs, inputs_max_voltages, stream_setting, resolution,
               scan_rate, sample_rate=-1) -> Tuple[int, int]:
        """
        Set up a connection to the LabJack for streaming

        Parameters
        ----------
        inputs: sequence of strings
            Names of input channels on the LabJack device to read.
            Must correspond to the actual name on the device.
        inputs_max_voltages: sequence of real values
            Maximum voltages corresponding element-wise to the channels
            listed in inputs.
        stream_setting: int, optional
            See official LabJack documentation.
        resolution: int, optional
            See official LabJack documentation.
        scan_rate: int
            Number of times per second (Hz) the device will get a datapoint for
            each of the channels specified.
        sample_rate: int, optional
            Number of data points contained in a packet sent by the LabJack
            device. -1 indicates the maximum possible sample rate.

        Returns
        -------
        scan_rate : int
            The actual scan rate the device starts at
        sample_rate : int
            The actual sample rate the device starts at

        """
        # Sanity check on inputs
        num_addresses: int = len(inputs)
        max_sample_rate: int = scan_rate * num_addresses

        if sample_rate == -1:
            sample_rate = max_sample_rate
        elif sample_rate > max_sample_rate:
            print("Sample rate is too high. Setting to max value.")
            sample_rate = max_sample_rate

        # Declare the ports we want to read, EG. AIN0 & AIN1
        scan_list = ljm.namesToAddresses(num_addresses, inputs)[0]

        # If a packet is lost, configure the device to try and get it again.
        ljm.writeLibraryConfigS("LJM_RETRY_ON_TRANSACTION_ID_MISMATCH", 1)

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
        names = ("AIN_ALL_NEGATIVE_CH",
                 *[element + "_RANGE" for element in inputs],
                 "STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX")
        values = (ljm.constants.GND, *inputs_max_voltages,
                  stream_setting, resolution)

        # Write the analog inputs' negative channels (when applicable),
        # ranges, stream settling time and stream resolution configuration.
        num_frames: int = len(names)
        ljm.eWriteNames(self.handle, num_frames, names, values)

        # Configure and start stream
        return ljm.eStreamStart(self.handle, sample_rate, num_addresses,
                                scan_list, scan_rate), sample_rate

    def collect_data(self,
                     inputs: List[str],
                     inputs_max_voltages: List[float],
                     seconds: float,
                     scan_rate: int,
                     sample_rate=-1,
                     stream_setting=0,
                     resolution=8,
                     verbose=False) -> Tuple[float, float]:
        """
        Collect data from the LabJack device.

        Data collection will overwrite any data stored in this object's
        internal array.

        Parameters
        ----------
        inputs : sequence of strings
            Names of input channels on the LabJack device to read.
            Must correspond to the actual name on the device.
        inputs_max_voltages : sequence of real values
            Maximum voltages corresponding element-wise to the channels
            listed in inputs.
        seconds : float
            Duration of the data run in seconds. The run will last at least as
            long as this value, and will try to stop streaming when this time
            has been met.
        scan_rate : int
            Number of times per second (Hz) the device will get a data point for
            each of the channels specified.
        sample_rate : int, optional
            Number of data points contained in a packet sent by the LabJack
            device. -1 indicates the maximum possible sample rate.
        stream_setting : int, optional
            See official LabJack documentation.
        resolution : int, optional
            See official LabJack documentation.
        verbose : str, optional
            If enabled, will print out statistics about each read.

        Returns
        -------
        tot_time : float
            The total amount of time actually spent collecting data
        num_skips : float
            The number of skipped data points.

        Examples
        --------
        Create a reader for a Labjack T7 and read off 60.5 seconds of data at
        50 kHz from channels AIN0, AIN1 which have a maximum voltage of 10V
        each:

        >>> reader = LabjackReader("T7")
        >>> reader.collect_data(["AIN0", "AIN1"], [10.0, 10.0], 60.5, 10000)
        None

        """
        # Open a connection.
        self._open_connection()

        # Close the stream if it was already open; this is done
        # to prevent unexpected termination from last time messing
        # up the connection this time.
        self._close_stream()

        num_addrs = len(inputs)

        scan_rate, sample_rate = self._setup(inputs, inputs_max_voltages,
                                             stream_setting, resolution,
                                             scan_rate,
                                             sample_rate=sample_rate)

        print("\nStream started with a scan rate of %0.0f Hz." % scan_rate)

        self.input_channels = inputs

        # Create a RawArray for multiple processes; this array
        # stores our data.
        size = int(seconds * scan_rate * (len(inputs) + 1))
        self.data_arr = RawArray('d', size)

        total_skip = 0  # Total skipped samples

        packet_num = 0
        self.max_index = 0
        step_size = len(inputs)

        # Python 3.7 has time_ns, upgrade to this when Conda supports it.
        start = time.time()
        while self.max_index < size:
            # Read all rows of data off of the latest packet in the stream.
            ret = ljm.eStreamRead(self.handle)
            curr_data = ret[0]

            if verbose:
                print("There are %d scans left on the device buffer",
                      "and %d scans left in the LJM's buffer", *ret[1:])

            # We will manually calculate the times each entry occurs at.
            # The stream itself is timed by the same clock that runs
            # CORE_TIMER, and it is officially advised we use the stream
            # clocking instead.
            # See https://forums.labjack.com/index.php?showtopic=6992
            for i in range(0, len(curr_data), step_size):
                curr_time = (sample_rate / scan_rate) * (packet_num + (i / len(curr_data)))

                if self.max_index >= size - step_size:
                    break

                # We get a giant 1D list back, so work with what we have.
                self.data_arr[self.max_index: self.max_index + step_size] =\
                    curr_data[i:i + step_size]
                self.max_index += step_size

                # Put in the time as well
                self.data_arr[self.max_index] = curr_time
                self.max_index += 1

            packet_num += 1

            # Count the skipped samples which are indicated by -9999 values
            # Missed samples occur after a device's stream buffer overflows
            # and are reported after auto-recover mode ends.
            curr_skip = curr_data.count(-9999.0)
            total_skip += curr_skip

            ainStr = ""
            for j in range(0, num_addrs):
                ainStr += "%s = %0.5f, " % (inputs[j], curr_data[j])
            if curr_skip:
                print("Scans Skipped = %0.0f" % (curr_skip/num_addrs))

        # We are done, record the actual ending time.
        end = time.time()

        tt = end - start
        if verbose:
            print("\nTotal scans = %i\
                   \nTime taken = %f seconds\
                   \nLJM Scan Rate = %f scans/second\
                   \nTimed Scan Rate = %f scans/second\
                   \nTimed Sample Rate = %f samples/second\
                   \nSkipped scans = %0.0f"
                  % (self.max_index, tt, scan_rate, (self.max_index / tt),
                     (self.max_index * num_addrs / tt),
                     (total_skip / num_addrs)))

        # Close the connection.
        self._close_stream()

        return tt, (total_skip / num_addrs)
