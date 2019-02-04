from labjack import ljm
import numpy as np
import pandas as pd
from typing import List, Tuple, Union
from math import ceil
import time
import datetime
from multiprocessing import RawArray
from colorama import init, Fore
init()


T7_TYPE = {"name": "T7",
           "command_response": {1: {"bits": 16,   "microvolts": 316,   "sample_time_ms": 0.04},
                                2: {"bits": 16.5, "microvolts": 223,   "sample_time_ms": 0.04},
                                3: {"bits": 17,   "microvolts": 158,   "sample_time_ms": 0.1},
                                4: {"bits": 17.5, "microvolts": 112,   "sample_time_ms": 0.1},
                                5: {"bits": 17.9, "microvolts": 84.6,  "sample_time_ms": 0.2},
                                6: {"bits": 18.3, "microvolts": 64.1,  "sample_time_ms": 0.3},
                                7: {"bits": 18.8, "microvolts": 45.3,  "sample_time_ms": 0.6},
                                8: {"bits": 19.1, "microvolts": 36.8,  "sample_time_ms": 1.1},
                                9: {"bits": 19.6, "microvolts": 26.0,  "sample_time_ms": 3.5},
                                10: {"bits": 20.5, "microvolts": 14.0, "sample_time_ms": 13.4},
                                11: {"bits": 21.3, "microvolts": 8.02, "sample_time_ms": 66.2},
                                12: {"bits": 21.4, "microvolts": 7.48, "sample_time_ms": 159},
                               }
            }
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
        device_type : str
            A LabJack model, such as T7, T4, or DIGIT
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
                and isinstance(identifier, str)
                or (device_type != "T7" or device_type != "T4")):
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
                f.write(",".join(self.input_channels) + ',time,system-time\n')
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
            row_width = len(self.input_channels) + 2
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

        row_width = len(self.input_channels) + 2
        max_row = int(max_row / row_width)

        if num_rows < -1:
            raise Exception("Invalid number of rows provided")
        elif num_rows == -1:
            return self._reshape_data(0, max_row)
        else:
            return self._reshape_data(max_row - num_rows, max_row)
    
    def get_dataframe(self):
        """
        Gets this object's recorded data in dataframe form.

        Parameters
        ----------
        None

        Returns
        -------
        table: dataframe
            A Pandas Dataframe with the following columns:
            AINB....AINC: Voltage values for the user-specified channels
                          AIN #B to #C.
            Time:  Recorded time (in seconds) of datapoints in row, as
                   observed by the LabJack
            System Time: Recorded time (in nanoseconds) of datapoints in
                         row, as observed by the host computer

        Notes
        -----
        If the internal data array has not been initialized yet, behavior
        is undefined.
        """
        return pd.DataFrame(self.get_data(-1),
                            columns=self.input_channels + ["Time", "System Time"])


    def _open_connection(self, verbose=True):
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
            if verbose:
                print("Opened a LabJack with Device type: %i,\n"
                    "Connection type: %i, Serial number: %i,\n"
                    "IP address: %s, Port: %i, Max bytes per MB: %i"
                    % (info[0], info[1], info[2],
                        ljm.numberToIP(info[3]), info[4], info[5]))

    def _close_stream(self, verbose=False) -> None:
        """
        Close a streaming connection to the LabJack.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        try:
            # Try to close the stream
            ljm.eStreamStop(self.handle)
            self.connection_open = False
            if verbose:
                print("\nStream stopped.")
        except:
            # No stream running, probably.
            if verbose:
                print("Could not stop stream, possibly because there is no stream running.")
            pass

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
    
    def find_max_freq(self,
                  inputs: List[str],
                  inputs_max_voltages: List[float],
                  stream_setting=0,
                  resolution=0,
                  verbose=True):
        """
        Determine the maximum frequency and number of elements per packet this
        device can sample at without overflowing any buffers.

        Parameters
        ----------
        inputs : sequence of strings
            Names of input channels on the LabJack device to read.
            Must correspond to the actual name on the device.
        inputs_max_voltages : sequence of real values
            Maximum voltages corresponding element-wise to the channels
            listed in inputs.
        stream_setting : int, optional
            See official LabJack documentation.
        resolution : int, optional
            See official LabJack documentation.
        verbose : str, optional
            If enabled, will print out statistics about each read.

        Returns
        -------
        scan_rate : int
            Number of times per second (Hz) the device will get a data point for
            each of the channels specified.
        sample_rate : int, optional
            Number of data points contained in a packet sent by the LabJack
            device.

        Examples
        --------
        Find out the maximum (Hz, items/packet) an arbitrary LabJack T7 can
        read from the channels AIN0, AIN1 each having a maximum voltage of
        10V.

        Output varies depending upon many factors, such as connection method
        to the LabJack, the device itself, and so forth.

        >>> reader = LabjackReader("T7")
        >>> reader.find_max_freq(["AIN0", "AIN1"], [10.0, 10.0])
        (57400.0, 1024)

        """
    
        self._close_stream()


        MAX_BUFFERSIZE = 2
        MAX_LJM_BUFFERSIZE = 2
        NUM_SECONDS = 30
        min_rate = 0
        med_rate = 100
        max_rate = 0

        exponential_mode = True

        # The number of elements we get back in a packet.
        start_sample_rate = 1

        last_good_rate = -1
        last_good_sample = -1

        while(1):
            # First, try to start at the rate specified.
            opened = False
            valid_config = False

            # Variables that are only there to show initial state for logging purposes
            print_packet_size = 0
            print_frequency = 0

            while not opened:
                try:
                    # Open a connection.
                    self._open_connection(verbose=False)
                    print("Trying to connect at %d Hz, %d" % (med_rate, start_sample_rate), end='')
                    scan_rate, sample_rate = self._setup(inputs,
                                                        inputs_max_voltages,
                                                        stream_setting,
                                                        resolution,
                                                        med_rate,
                                                        sample_rate=start_sample_rate)
                except:
                    print(Fore.RED + "...failed." + Fore.RESET)
                    if start_sample_rate < med_rate:
                        # First, try increasing the number of elements per packet.
                        start_sample_rate = min(2 * start_sample_rate, med_rate)
                    else:
                        # Step down, and turn off exponential mode
                        exponential_mode = False
                        start_sample_rate = 1
                        max_rate = med_rate
                        med_rate = (min_rate + med_rate) / 2

                        if (int(med_rate) == int(min_rate)
                        or int(med_rate) == int(max_rate)):
                            self._close_stream()
                            return last_good_rate - (last_good_rate % 100), last_good_sample
                else:
                    opened = True
                    print_packet_size = start_sample_rate
                    print_frequency = med_rate
                    print(Fore.GREEN + "...opened." + Fore.RESET)

            iterations = 0
            buffer_size = 0
            num_skips = 0
            ljm_buffer_size = 0
            max_buffer_size = 0
        
            try:
                while iterations < NUM_SECONDS * scan_rate:
                    # Read all rows of data off of the latest packet in the stream.
                    ret = ljm.eStreamRead(self.handle)
                    buffer_size = ret[1]
                    ljm_buffer_size = max(ljm_buffer_size, ret[2])
                    num_skips = ret[0].count(-9999.0)
                    max_buffer_size = max(max_buffer_size, buffer_size)
                    iterations += len(ret[0])

                    if buffer_size >= MAX_BUFFERSIZE or num_skips or ljm_buffer_size >= MAX_LJM_BUFFERSIZE:
                        if start_sample_rate < med_rate:
                            # First, try increasing the number of elements per packet.
                            start_sample_rate = min(2 * start_sample_rate, med_rate)
                        else:
                            # Step down, and turn off exponential mode
                            start_sample_rate = 1
                            max_rate = med_rate
                            med_rate = (min_rate + med_rate) / 2
                            exponential_mode = False

                            if (int(med_rate) == int(min_rate)
                                or int(med_rate) == int(max_rate)):
                                # Go to last good and terminate.
                                self._close_stream()
                                return last_good_rate - (last_good_rate % 100), last_good_sample

                        # In all cases, try again.
                        break

            except ljm.LJMError:
                if start_sample_rate < med_rate:
                    # First, try increasing the number of elements per packet.
                    start_sample_rate = min(2 * start_sample_rate, med_rate)
                else:
                    # Step down, and turn off exponential mode
                    start_sample_rate = 1
                    max_rate = med_rate
                    med_rate = (min_rate + med_rate) / 2
                    exponential_mode = False
                    break
            else:
                if (buffer_size < MAX_BUFFERSIZE
                    and not num_skips
                    and ljm_buffer_size < MAX_LJM_BUFFERSIZE):
                    # Store these working values
                    last_good_rate = med_rate
                    last_good_sample = start_sample_rate
                    valid_config = True
        
                    if exponential_mode:
                        # Exponentially (const * 2^n) increase the upper
                        # search bound. Recalculate the midpoint.
                        min_rate = med_rate
                        max_rate = 2 * med_rate
                        med_rate = 1.5 * med_rate
                    else:
                        # Step up
                        min_rate = med_rate
                        med_rate = (max_rate + med_rate) / 2

                    if (int(med_rate) == int(min_rate)
                    or int(med_rate) == int(max_rate)):
                        self._close_stream()
                        return last_good_rate - (last_good_rate % 100), last_good_sample
            finally:
                self._close_stream()
                if verbose:
                    print(Fore.GREEN + "[PASS]" if valid_config else Fore.RED + "[FAIL]",
                          Fore.RESET + "Finished a stream with an effective scan rate of %5.0f Hz @ %5d points / packet; "
                          "buffer had at most %s%3d%s items remaining. Frequency search range is now [%5d, %5d]." % (scan_rate, print_packet_size, (Fore.RED if max_buffer_size >= MAX_BUFFERSIZE else Fore.RESET), max_buffer_size, Fore.RESET, min_rate, max_rate),
                          "There were " + (Fore.RED if num_skips else Fore.RESET) + str(num_skips) + Fore.RESET + " skips."
                          + " LJM max size was %d" % ljm_buffer_size)


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

        total_skip = 0  # Total skipped samples

        packet_num = 0
        self.max_index = 0
        step_size = len(inputs)

        # Create a RawArray for multiple processes; this array
        # stores our data.
        size = int(seconds * scan_rate * (len(inputs) + 2))
    
        self.data_arr = RawArray('d', int(size))

        # Python 3.7 has time_ns, upgrade to this when Conda supports it.
        start = time.time_ns()
        while self.max_index < size:
            # Read all rows of data off of the latest packet in the stream.
            ret = ljm.eStreamRead(self.handle)
            curr_data = ret[0]

            if verbose:
                print("[%s] (%d/%d) (%d) (%d) There are %d scans left on the device buffer and %d scans left in the LJM's buffer" % (datetime.datetime.now(), self.max_index, size, size - self.max_index, len(curr_data), ret[1], ret[2]))

            # Ensure that this packet won't overflow our buffer.
            if self.max_index + ((len(curr_data) / step_size) * (2 + step_size)) > size:
                break

            for i in range(0, len(curr_data), step_size):
                # We will manually calculate the times each entry occurs at.
                # The stream itself is timed by the same clock that runs
                # CORE_TIMER, and it is officially advised we use the stream
                # clocking instead.
                # See https://forums.labjack.com/index.php?showtopic=6992
                curr_time = (sample_rate / scan_rate) * (packet_num + (i / len(curr_data)))

                # We get a giant 1D list back, so work with what we have.
                self.data_arr[self.max_index: self.max_index + step_size] =\
                    curr_data[i:i + step_size]
                self.max_index += step_size

                # Put in the time as well
                self.data_arr[self.max_index] = curr_time
                self.max_index += 1
                self.data_arr[self.max_index] = time.time_ns() - start
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
        end = time.time_ns()

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
