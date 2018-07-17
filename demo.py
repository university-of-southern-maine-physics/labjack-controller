"""
Demonstrates the functionality of the LabjackReader.

Creates a Tkinter GUI that prompts the user to set the frequency of data
collection, the channels they will be sampling from, the duration of
observing, and the filename to write this observed data to.

After this input has been given, the GUI will close, and realtime data
recording, backup, and graphing will begin.
"""
from labjackcontroller.labtools import LabjackReader
from multiprocessing.managers import BaseManager
from multiprocessing import Process

from tkinter import Tk, Button, Scale, Frame, Entry, \
                    OptionMenu, Checkbutton, HORIZONTAL, LEFT, RIGHT, END, \
                    IntVar, StringVar

import time
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt


class TKWindow:
    def __init__(self, width=1366, height=768) -> None:
        self.im_width = width
        self.im_height = height

        # Declare the existence/init values of the class vars we'll use
        self.master = Tk()
        self.duration = IntVar()
        self.start_time = StringVar()
        self.filename = StringVar()
        self.connection_type = StringVar()
        self.device_type = StringVar()

        # Checkbox IntVars for four channels
        self.ain_0, self.ain_1 = IntVar(), IntVar()
        self.ain_2, self.ain_3 = IntVar(), IntVar()

        # Set three of them to be checked.
        self.ain_0.set(1)
        self.ain_1.set(1)
        self.ain_2.set(1)

        self.channels = []

        # Set default values.
        self.connection_type.set("ETHERNET")
        self.device_type.set("T7")

        # Window header
        self.master.title("Torsion Pendulum Data Window")

        # First frame to hold sliders
        self.inter_container = Frame(self.master)
        self.inter_container.pack()

        # Slider for frequency of data sampling
        self.freq_slider = Scale(self.inter_container, from_=2, to=50000,
                                 label="Frequency (Hz)", length=0.95*width,
                                 resolution=10,
                                 orient=HORIZONTAL)
        self.freq_slider.set(30000)
        self.freq_slider.pack(side=LEFT)

        # Second frame to hold buttons
        self.button_container = Frame(self.master)
        self.button_container.pack()

        # Textbox to get how long this data sampling should run.
        duration_box = Entry(self.button_container, textvariable=self.duration)

        # Remove the default text of 0 and replace it with a meaningful
        # message
        duration_box.delete(0, END)
        duration_box.insert(0, "duration (seconds)")
        duration_box.pack(side=LEFT)

        start_time_box = Entry(self.button_container,
                               textvariable=self.start_time)
        start_time_box.delete(0, END)
        start_time_box.insert(0, "Start (optional, hh:mm, 24hr)")
        start_time_box.pack(side=RIGHT)

        # Dropdown to select the connection type
        connection_type_dropdown = OptionMenu(self.button_container,
                                              self.connection_type,
                                              *["ETHERNET", "USB", "ANY"])
        connection_type_dropdown.pack(side=RIGHT)

        # Dropdown to select the device type we're connecting to.
        device_type_dropdown = OptionMenu(self.button_container,
                                          self.device_type,
                                          *["T7", "T4"])
        device_type_dropdown.pack(side=LEFT)

        # Third frame to hold channel checkboxes.
        self.filename_container = Frame(self.master)
        self.filename_container.pack()

        # Textbox to get a filename for this datarun
        filename_box = Entry(self.filename_container,
                             textvariable=self.filename)

        # Remove the default text of 0 and replace it with a meaningful
        # message
        filename_box.delete(0, END)
        filename_box.insert(0, "filename")
        filename_box.pack(side=LEFT)

        # Fourth frame to hold channel checkboxes.
        self.check_container = Frame(self.master)
        self.check_container.pack()

        # All the checkboxes we'll need.
        self.ain_0_box = Checkbutton(self.check_container, text="AIN0",
                                     variable=self.ain_0)
        self.ain_0_box.pack(side=LEFT)

        self.ain_1_box = Checkbutton(self.check_container, text="AIN1",
                                     variable=self.ain_1)
        self.ain_1_box.pack(side=LEFT)

        self.ain_2_box = Checkbutton(self.check_container, text="AIN2",
                                     variable=self.ain_2)
        self.ain_2_box.pack(side=LEFT)

        self.ain_3_box = Checkbutton(self.check_container, text="AIN3",
                                     variable=self.ain_3)
        self.ain_3_box.pack(side=LEFT)

        # Button to run data collection.
        self.start_button = Button(self.master, text="Start Run",
                                   command=self.graph)
        self.start_button.pack()

        # From now on, update the GUI to always have valid params.
        self.update_gui()
        self.master.mainloop()

    def graph(self) -> None:
        """ Closes GUI and starts LabJack with user's parameters """

        # Find out what channels were selected by the user.
        channels = [label for value, label in
                    zip([self.ain_0.get(), self.ain_1.get(),
                         self.ain_2.get(), self.ain_3.get()],
                        ["AIN0", "AIN1", "AIN2", "AIN3"]) if value]

        # Get the other variables they specified.
        filename = self.filename.get()
        duration = self.duration.get()
        frequency = self.freq_slider.get()
        device_type = self.device_type.get()
        connection_type = self.connection_type.get()

        # Close the GUI, as the mainloop in Tk is blocking.
        self.master.destroy()

        # Register the LabjackReader so we can share it across processes.
        BaseManager.register('LabjackReader', LabjackReader)
        manager = BaseManager()
        manager.start()

        # Instantiate a shared LabjackReader
        my_lj = manager.LabjackReader(device_type, connection=connection_type)

        # Declare a data-gathering process
        data_proc = Process(target=my_lj.collect_data,
                            args=(channels, [10.0]*len(channels), duration,
                                  frequency),
                            kwargs={'resolution': 0})

        # Declare a graphing process
        graph_proc = Process(target=plotting_func, args=(my_lj, duration,
                                                         frequency))

        # Declare a data backup process
        backup_proc = Process(target=backup, args=(my_lj, frequency, filename,
                                                   duration))

        # Start all threads, and join when finished.
        data_proc.start()
        graph_proc.start()
        backup_proc.start()

        data_proc.join()
        graph_proc.join()
        backup_proc.join()

    def update_gui(self) -> None:
        """ Updates GUI elements to always have valid values."""

        channel_sum = self.ain_0.get() + self.ain_1.get() \
            + self.ain_2.get() + self.ain_3.get()
        if not channel_sum:
            self.freq_slider.config(to=0)
        elif channel_sum == 1:
            self.freq_slider.config(to=105000)
        elif channel_sum == 2:
            self.freq_slider.config(to=75000)
        elif channel_sum == 3:
            self.freq_slider.config(to=36000)
        elif channel_sum == 4:
            self.freq_slider.config(to=25000)

        # Update in the next ms.
        self.master.after(1, self.update_gui)


def backup(labjack: LabjackReader, backup_amt: int,
           filename: str, num_seconds: int) -> None:
    """
    Backup data realtime.

    Parameters
    ----------
    labjack: LabjackReader
        A LabjackReader that is collecting data at the
        time of this function's call.
    backup_amt: int
        Number of rows to back up every attempt
    filename: str
        The name of the file to write to.
        If it does not exist yet, it will be created.
    num_seconds: int
        The number of seconds to try realtime backup.
        After this time, write any remaining data in
        the labjack's buffer.

    Returns
    -------
    None

    """
    start_pos = 0
    start_time = time.time()

    # Write header only. The labjack may not be initialized yet, so keep
    # trying until it works.
    while labjack.save_data(filename, 0, 0, mode='w', header=True) < 0:
        continue

    # Write data until time is up.
    while time.time() - start_time <= num_seconds:
        if labjack.get_max_row() > start_pos:
            print("Backup at", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
            print("Running from", start_pos, "to", start_pos + backup_amt)
            start_pos += labjack.save_data(filename,
                                           start_pos,
                                           start_pos + backup_amt,
                                           mode='a')
    print("Saving from rows", start_pos, "to", labjack.get_max_row())

    # Save the rest
    labjack.save_data(filename, start_pos,
                      labjack.get_max_row() + 1,
                      mode='a')


def plotting_func(labjack: LabjackReader, num_seconds: int, sample_rate: int):
    """ Plot data realtime """
    plt.figure(figsize=(16, 9))
    plt_handle = plt.gcf()
    plt_handle.subplots_adjust(bottom=0.2)
    ax = plt_handle.add_subplot(111)
    plt_handle.show()

    start_time = time.time()
    while time.time() - start_time <= num_seconds:
        data = labjack.get_data(sample_rate)
        if data is None:
            continue
        ax.clear()

        unzipped = list(zip(*data[::int(sample_rate/100)]))
        t_arr = unzipped[-1]
        for sig in unzipped[:-1]:
            ax.plot(t_arr, sig)
        plt_handle.canvas.draw()


if __name__ == "__main__":
    gui = TKWindow()
