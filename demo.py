from labjackcontroller.labtools import LabjackReader
from multiprocessing.managers import BaseManager
from multiprocessing import Process

import time

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

def plotting_func(labjack, num_seconds):
    plt.figure(figsize=(16, 9))
    plt_handle = plt.gcf()
    ax = plt_handle.add_subplot(111)
    plt_handle.show()

    start_time = time.time()
    while time.time() - start_time <= num_seconds:
        if labjack.get_data() is None:
            continue
        ax.clear()
        s_arr, t_arr = list(zip(*labjack.get_data()))
        ax.plot(t_arr, s_arr)
        plt_handle.canvas.draw()


BaseManager.register('LabjackReader', LabjackReader)
manager = BaseManager()
manager.start()
my_lj = manager.LabjackReader("T7")

data_func = lambda obj, *args: obj.collect_data(*args, 
                                                resolution=0,
                                                scans_per_read=512)
data_proc = Process(target=data_func, args=(my_lj, ["AIN0"], [10], 300, 40000))
graph_proc = Process(target=plotting_func, args=(my_lj, 300))
data_proc.start()
graph_proc.start()
data_proc.join()
graph_proc.join()


