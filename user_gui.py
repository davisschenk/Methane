#!/usr/bin/env python3

import time
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use("TkAgg") # set the backend
import matplotlib.style as mplstyle
import requests
mplstyle.use('fast')

import fileinput
from itertools import cycle
import json

address = "http://192.168.8.209:8008"
matplotlib.rcParams['toolbar'] = 'None'

plt.show()
print("Show")

# fig = plt.figure(num = " ",figsize =(11.75, 10))
# plt.get_current_fig_manager().window.wm_geometry("+725+20")

fi = cycle(fileinput.FileInput(["data"]))
while True:
    # shared = requests.get(address)
    # print(shared.text)
    # shared = shared.json()
    shared = json.loads(next(fi))
    print(shared)
    try:
        g = shared.get('Selection_graph', 1)
        if g == 1:
            plt.cla()
            plt.grid()
            data = shared.get('Data')

            if data is not None:
                plt.plot(data, linewidth=2,color='black')
                plt.xlabel("Data Points", fontsize = 18)
                plt.ylabel("Detector Signal (mV)", fontsize = 18)
                plt.xticks(fontsize = 12)
                plt.yticks(fontsize = 12)
                plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.1)
            plt.draw()
            plt.pause(0.05)

        if g == 2:
            data = shared.get('Data')
            data2 = shared.get('Fit')
            data3 = shared.get('InitGuess')
            plt.cla()
            plt.grid()
            if data is not None and data2 is not None:
                plt.plot(data, label = "Raw Data", linewidth=1,color="black")
                plt.plot(data2, label = "Fit", linewidth=4,color="red",alpha = 0.3)
                plt.plot(data3, label = "Init Guess", linewidth=1,color="green")
                plt.xlabel("Data Points", fontsize = 18)
                plt.ylabel("Detector Signal (mV)", fontsize = 18)
                plt.xticks(fontsize = 12)
                plt.yticks(fontsize = 12)
                plt.legend(fontsize = 12)

            plt.draw()
            plt.pause(0.05)

        if g == 3:
            data = shared.get('CH4_array')
            xx = shared.get('ET_array')
            plt.cla()
            plt.grid()
            if data is not None and xx is not None:
                plt.plot(xx,data, linewidth=2,color="blue")
                plt.xlabel("Elapsed Time (s)", fontsize = 18)
                plt.ylabel("CH4 (ppb)", fontsize = 18)
                plt.title("CH4 Timechart", fontsize = 18)
                plt.xticks(fontsize = 12)
                plt.yticks(fontsize = 12)
                plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.1)
            plt.draw()
            plt.pause(0.05)

        if g == 4:
            data = shared.get('Water_array')
            xx = shared.get('ET_array')
            plt.cla()
            plt.grid()
            if data is not None and xx is not None:
                plt.plot(xx,data, linewidth=2,color="black")
                plt.xlabel("Elapsed Time (s)", fontsize = 18)
                plt.ylabel("Water (ppm)", fontsize = 18)
                plt.title("Water Timechart", fontsize = 18)
                plt.xticks(fontsize = 12)
                plt.yticks(fontsize = 12)
                plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.1)
            plt.draw()
            plt.pause(0.05)

        if g == 5:
            data = shared.get('Residual')
            plt.cla()
            plt.grid()
            if data is not None:
                plt.plot(data, linewidth=2,color="black")
                plt.xlabel("Data Points", fontsize = 18)
                plt.ylabel("Residual (mV)", fontsize = 18)
                plt.title("Residual", fontsize = 18)
                plt.xticks(fontsize = 12)
                plt.yticks(fontsize = 12)
                plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.1)
            plt.draw()
            plt.pause(0.05)


        time.sleep(1)

    except Exception as e:
        print ("Error in GUI_plot:  ",e)
        time.sleep(1)
