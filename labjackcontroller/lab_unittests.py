import unittest
from itertools import product
import numpy as np
from labjackcontroller.labtools import LabjackReader


class TestLJR(unittest.TestCase):

    def setUp(self):
        self.valid_device = "T7"
        self.valid_connection = LabjackReader(self.valid_device)

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
    
    def test_collection(self):
        for args in product([["AIN0"], ["AIN1"]], [[10.0], [1]],
                            np.linspace(0.001, 2, 50), range(1, 100000, 1000)):
            self.valid_connection.collect_data(*args)

    def test_file_write(self):
        # There should be no data, so we expect an exception.
        self.tmp_ljr = LabjackReader(self.valid_device)

        with self.assertRaises(Exception):
            self.valid_connection.write_data_to_file("tmp")
        # Test valid
        #self.valid_connection.write_data_to_file("tmp")
        #self.assertRaises(Exception)

if __name__ == '__main__':
    unittest.main()