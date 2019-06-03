import pytest
import itertools
import numpy as np
from labjackcontroller.labtools import LabjackReader, LJMLibrary


@pytest.fixture(scope='session')
def get_ljm_devices():
    return LJMLibrary().list_all()


@pytest.fixture(scope='session')
def ljm_all_channels():
    channels = [*["AIN" + str(num) for num in range(0, 1)],
                *["DIO" + str(num) for num in range(0, 1)]]
    return [subset for num_ch in range(1, len(channels) + 1)
            for subset in itertools.combinations(channels, num_ch)]


@pytest.fixture(scope='session')
def get_init_parameters(get_ljm_devices):
        return [[*row[:3], None] for row in get_ljm_devices] + \
              [("ANY", "ANY", "ANY", None),
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


def test_open_close_status(get_ljm_devices):
    for device_args in get_ljm_devices:
        curr_device = LabjackReader(*device_args[:3])

        for i in range(0, 10):
            curr_device.open()

            assert curr_device.connection_status

            curr_device.close()


@pytest.mark.parametrize("resolution", range(1, 8))
@pytest.mark.parametrize("frequency", [10, 100, 1000])
def test_collect_data_gathering(get_ljm_devices, ljm_all_channels, resolution,
                                frequency):
    # Duration of each test, in seconds.
    duration = 1

    for device_args in get_ljm_devices:
        curr_device = LabjackReader(*device_args[:3])

        for channel_config in ljm_all_channels:
            # Iterate through some amount of channels.
            print("Starting with channels", channel_config)
            tot_time, num_skips = curr_device \
                .collect_data(channel_config,
                              [10.0] * len(channel_config),
                              duration, frequency,
                              resolution=resolution,
                              verbose=False)
            device_shape = np.shape(curr_device.to_array(mode="all"))
            expected_shape = (frequency * duration, len(channel_config) + 2)

            assert device_shape == expected_shape
            assert num_skips == 0
            assert tot_time > duration - 0.01


@pytest.mark.parametrize("inputs, inputs_max_voltages, seconds, frequency,"
                         " scans_per_read, resolution,"
                         " expected_err",
                         [(["AIN0"], [10.0], 1, 1000, 500, 1, None)])
def test_collect_data_parameters(get_ljm_devices, inputs, inputs_max_voltages,
                                 seconds, frequency, scans_per_read,
                                 resolution, expected_err):
    if not len(get_ljm_devices):
        return

    if expected_err:
            with pytest.raises(expected_err):
                with LabjackReader(*get_ljm_devices[0][:3]) as curr_device:
                    curr_device.collect_data(inputs, inputs_max_voltages,
                                             seconds, frequency,
                                             scans_per_read=scans_per_read,
                                             resolution=resolution)
    else:
        with LabjackReader(*get_ljm_devices[0][:3]) as curr_device:
            curr_device.collect_data(inputs, inputs_max_voltages,
                                     seconds, frequency,
                                     scans_per_read=scans_per_read,
                                     resolution=resolution)


def test_callbacks(get_ljm_devices):
    for device_args in get_ljm_devices:
        # First test with no data stored.
        curr_device = LabjackReader(*device_args[:3])

        channels_to_scan = ["AIN0", "AIN2", "AIN4"]

        # Scan for 1 second at 10 Hz.
        curr_device.collect_data(channels_to_scan, 3 * [10.0], 1, 10,
                                 callback_function=new_callback)

        # Should return back our 3 data column and 2 time columns.
        assert np.shape(curr_device.to_array(mode="all")) == (10, 5)


def new_callback(row):
    # This function belongs to test_callbacks above.
    # We expect 3 channels, plus two for time.
    assert len(row) == 5


def test_to_array(get_ljm_devices):
    for device_args in get_ljm_devices:
        # First test with no data stored.
        curr_device = LabjackReader(*device_args[:3])

        assert curr_device.to_array(mode="all") is None
        assert curr_device.to_array(mode='relative', num_rows=50) is None
        assert curr_device.to_array(mode='range', start=17, end=65) is None

        # Scan for 1 second at 10 Hz.
        curr_device.collect_data(["AIN0"], [10.0], 1, 10)

        # Should return back our 1 data column and 2 time columns.
        assert np.shape(curr_device.to_array(mode="all")) == (10, 3)

        assert np.shape(curr_device
                        .to_array(mode='relative', num_rows=5)) == (5, 3)

        assert np.shape(curr_device
                        .to_array(mode='range', start=2, end=4)) == (2, 3)

        # The following should fail.
        with pytest.raises(Exception):
            curr_device.to_array(mode='relative', num_rows=12)

        with pytest.raises(Exception):
            curr_device.to_array(mode='range', start=2, end=40)

        with pytest.raises(Exception):
            curr_device.to_array(mode='range', start=-30, end=40)

        with pytest.raises(Exception):
            curr_device.to_array(mode='range', start=-30, end=4)
