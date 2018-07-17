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
        valid_scan_rate = 50  # Hz
        tot_scans, tot_time, num_skips =\
            self.valid_connection.collect_data(self.valid_channels,
                                               valid_max_voltages,
                                               valid_seconds,
                                               valid_scan_rate)
        return tot_scans, tot_time, num_skips

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
        self.valid_connection._open_stream()

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
        for _ in range(5):
            self.populate_valid_labjack()

    def test_file_write(self):
        self.populate_valid_labjack()

        # Our populated LJR should work.
        self.assertEqual(self.valid_connection.save_data("tmp", 0, 10), 10)

        # There should be no data, so we expect an exception.
        tmp_ljr = LabjackReader(self.valid_device)

        # Save the first 10 rows. Should return and say it was able to save
        # "error" rows, or -1
        self.assertEqual(tmp_ljr.save_data("tmp", 0, 10), -1)
    
    def test_reshaping(self):
        tot_scans, tot_time, num_skips = self.populate_valid_labjack()

        num_chanels_sampled = len(self.valid_channels)
        self.assertEqual(tot_scans * num_chanels_sampled /
                         (num_chanels_sampled + 1),
                         self.valid_connection.get_max_row())


if __name__ == '__main__':
    unittest.main()
