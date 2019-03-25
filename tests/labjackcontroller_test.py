import pytest
import numpy as np
from labjackcontroller.labtools import LabjackReader, ljm_reference


@pytest.fixture(scope='session')
def get_ljm_devices():
    return ljm_reference.list_all()


@pytest.fixture(scope='session')
def get_init_parameters(get_ljm_devices):
        return [[*row[:3], None] for row in get_ljm_devices] + \
              [("ANY", "ANY", "ANY", None if len(get_ljm_devices) else Exception),
               ('BAD', 'BAD', 'BAD', ValueError),
               ('T4', 'BAD', 'BAD', ValueError),
               (123, 'USB', 'BAD', TypeError),
               ('T7', 123, 'BAD', TypeError),
               (['T7'], 'USB', 'BAD', TypeError)]


def test_init(get_init_parameters):
    for data in get_init_parameters:
        dev, conn, d_id, expected_err = data

        if expected_err:
            with pytest.raises(expected_err):
                LabjackReader(dev, connection_type=conn,
                              device_identifier=d_id)
        else:
            assert isinstance(LabjackReader(dev, connection_type=conn,
                                            device_identifier=d_id),
                              LabjackReader)


def test_connection_release(get_ljm_devices):
    """
    LJM devices can only be used on a one-reciever-per-protocol basis.

    Makes sure we properly release these devices on deletion.
    """
    for device_args in get_ljm_devices:
        curr_device = LabjackReader(*device_args[:3])

        del curr_device

        # Resource should be freed for re-use.
        LabjackReader(*device_args[:3])


def test_open_close(get_ljm_devices):
    for device_args in get_ljm_devices:
        curr_device = LabjackReader(*device_args[:3])

        for i in range(0, 10):
            curr_device._open_connection()

            assert curr_device.connection_status

            curr_device._close_stream()


def test_to_list(get_ljm_devices):
    for device_args in get_ljm_devices:
        # First test with no data stored.
        curr_device = LabjackReader(*device_args[:3])

        assert curr_device.to_list(mode="all") is None
        assert curr_device.to_list(mode='relative', num_rows=50) is None
        assert curr_device.to_list(mode='range', start=17, end=65) is None

        # Scan for 1 second at 10 Hz.
        curr_device.collect_data(["AIN0"], [10.0], 1, 10)

        # Should return back our 1 data column and 2 time columns.
        assert np.shape(curr_device.to_list(mode="all")) == (10, 3)

        assert np.shape(curr_device.to_list(mode='relative', num_rows=5)) == (5, 3)

        assert np.shape(curr_device.to_list(mode='range', start=2, end=4)) == (2, 3)

        # The following should fail.
        with pytest.raises(Exception):
            curr_device.to_list(mode='relative', num_rows=12)

        with pytest.raises(Exception):
            curr_device.to_list(mode='range', start=2, end=40)

        with pytest.raises(Exception):
            curr_device.to_list(mode='range', start=-30, end=40)

        with pytest.raises(Exception):
            curr_device.to_list(mode='range', start=-30, end=4)
