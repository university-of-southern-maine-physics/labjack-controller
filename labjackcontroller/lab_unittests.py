import unittest
from labjackcontroller.labtools import LabjackReader


class TestLJR(unittest.TestCase):

    def setUp(self):
        self.valid_device = "T7"
        self.valid_connection = LabjackReader(self.valid_device)
        self.valid_channels = ["AIN0", "AIN1", "AIN2"]

    def populate_valid_labjack(self):
        valid_max_voltages = [10.0, 10.0, 10.0]
        valid_seconds = 5
        valid_scan_rate = 100  # Hz
        tot_time, num_skips =\
            self.valid_connection.collect_data(self.valid_channels,
                                               valid_max_voltages,
                                               valid_seconds,
                                               valid_scan_rate)
        return tot_time, num_skips

    def test_init(self):
        # Device handles that should fail.
        with self.assertRaises(Exception):
            for device_name in [1, 3j, self.valid_connection]:
                LabjackReader(device_name)

        # Also, check our "safe" instance
        self.assertIsInstance(self.valid_connection, LabjackReader)

        # Check connection types. Should fail silently until we try
        # to get data.
        for connection_type in ["ANY", "ETHERNET", "USB", "WIFI"]:
            tmp_ljm = LabjackReader(self.valid_device,
                                    connection=connection_type)
            self.assertIsInstance(tmp_ljm, LabjackReader)

    def test_close(self):
        # Ensures we can perform a meaningless close without
        # throwing anything.
        self.valid_connection._close_stream()

    def test_open(self):
        # Ensures we can perform a meaningless open without
        # throwing anything.
        self.valid_connection._open_connection()

        # This leaves a connection standing open.

    def test_data_collection(self):
        valid_channels = ["AIN0", "AIN1", "AIN2"]
        valid_max_voltages = [10.0, 10.0, 10.0]
        valid_seconds = 5
        valid_scan_rate = 50  # Hz

        self.populate_valid_labjack()

        invalid_connection = LabjackReader("Fake")

        with self.assertRaises(Exception):
            # First, test an invalid connection
            invalid_connection.collect_data(valid_channels,
                                            valid_max_voltages,
                                            valid_seconds,
                                            valid_scan_rate)

        # Now, test a valid connection multiple times.
        for _ in range(4):
            self.populate_valid_labjack()

        # Assert there is no skipping.
        self.assertEqual(self.populate_valid_labjack()[1], 0)

    def test_reshaping(self):
        tot_time, num_skips = self.populate_valid_labjack()


if __name__ == '__main__':
    unittest.main()
