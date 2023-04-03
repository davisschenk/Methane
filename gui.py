import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import requests

#matplotlib.use("Qt4Agg")
#from matplotlib.backends.backend_qt4agg import FigureCanvas
#from matplotlib import pyplot as plt

import tkinter as tk
from tkinter import ttk

import time

address = "http://192.168.8.209:8008"

def get_data():
    data =  requests.get(address).json()
    data.update({"Status": "OK"})

    return data

shared = get_data()

# setup GUI
style.use("ggplot")
fig = Figure(figsize=(20,9))
#fig = plt.figure()
ax = fig.add_subplot(111)

line, = ax.plot([], linewidth=10, c='b')
num_pts_to_plot = 50
ax.set_xlim(0,num_pts_to_plot)
ax.axes.xaxis.set_ticklabels([])
ax.set_xlabel('Elapsed time', size=40)
min_y_max = 4     # set min_y_max, prev_y_max, and curr_y_max to the same number
prev_y_max = 4    # set min_y_max, prev_y_max, and curr_y_max to the same number
curr_y_max = 4    # set min_y_max, prev_y_max, and curr_y_max to the same number
ax.set_ylim([-0.1, curr_y_max*1.1])
ax.yaxis.set_tick_params(labelsize=40)
ax.set_ylabel('Methane [ppb]', size=40)

#plt.show(block=False)

varlist = ['Methane [ppb]', 'Battery','Status']

namelist = ["Methane", "Battery","Status"]

ani_obj_ref = None # need to keep a reference to the animation object that gets created
x = []
i = 0
et_list = []
meth_conc_list = []

prev_time = time.time()

def animate(i, table):
    global prev_time, shared
    shared = get_data()
    #print("time diff: " + str(time.time() - prev_time) + "\t" + str(shared.get("Methane")))

    # update table
    table.delete("values")
    table.insert('', 'end', "values", values=(shared.get("Methane"),
                                              shared.get("Battery"),
                                              shared.get("Status")))

    #datalist = list(shared.get_multi(varlist).values())
    #for index in range (0, len(varlist)):
        #table.delete(varlist[index])
        #table.insert('', 'end', varlist[index], values=(namelist[index],datalist[index]))

    # update graph
    # when methane data array is initialized, it has length < 100
    # populate x array once per iteration to match size of methane data array (for plotting)
    if len(x) < num_pts_to_plot:
        x.append(i)
        i += 1

    # get data
    et = shared.get('ElapsedTime')
    methane = shared.get('Methane')
    et_list.append(et)
    meth_conc_list.append(methane)
    # only plot the last certain number of data points
    if len(et_list) > num_pts_to_plot:
        et_list.pop(0)
        meth_conc_list.pop(0)

    # change Y limits of graph as necessary
    global prev_y_max, curr_y_max
    prev_y_max = curr_y_max
    curr_y_max = max(meth_conc_list)

    if curr_y_max < min_y_max:
        if (prev_y_max > min_y_max):
            ax.set_ylim([-0.1, min_y_max])
    else:
        ax.set_ylim([-0.1, max(meth_conc_list)*1.1])

    if curr_y_max > 10000:
        ax.set_facecolor("pink")
    else:
        ax.set_facecolor("lightgray")

    line.set_data(x[::1], meth_conc_list[::1])
    #line.set_data(et, meth_conc_list)
    ax.draw_artist(line)

    fig.canvas.draw()
    fig.canvas.flush_events()
    prev_time = time.time()


class MethaneGUIApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # setup screen size
        tk.Tk.wm_title(self, "Nikira Labs Portable Methane Analyzer (SN: NIK-PMA-10001)")
        screen_width = tk.Tk.winfo_screenwidth(self)
        screen_height = tk.Tk.winfo_screenheight(self)
        geometry = str(screen_width) + "x" + str(screen_height)
        tk.Tk.geometry(self, geometry)

        # "Starting Up..." screen
        self.start_frame = tk.Frame(self)
        self.start_label = tk.Label(self.start_frame, text="Methane Analyzer Starting Up...", font=('Helvetica 60 bold'))
        self.start_label.pack(pady=((screen_height/2) - 80))
        self.start_frame.pack()
        self.start_frame.tkraise()

        # start analyzer GUI after certain delay
        delay_ms = 1000
        self.after(delay_ms, self.start_analyzer_gui)

    def start_analyzer_gui(self):
        # remove starting screen
        self.start_label.pack_forget()
        self.start_frame.pack_forget()
        self.start_label.destroy()
        self.start_frame.destroy()

        # initialize container for GUI
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        #self.container.grid_rowconfigure(0, weight=4)
        #self.container.grid_rowconfigure(1, weight=5)
        #self.container.grid_columnconfigure(0, weight=1)

        # initialize frame for data table
        self.table_frame = DataTableFrame(self.container, self)
        self.table_frame.config(height=1, width=1)
        self.table = self.table_frame.get_table()
        self.table_frame.pack()
        #self.table_frame.grid(row=0, column=0, sticky="nsew")

        # initialize frame for graph
        self.graph_frame = GraphFrame(self.container, self)
        self.graph_frame.pack()
        #self.graph_frame.grid(row=1, column=0, sticky="sew")

        # need to keep a reference to the Animation object that gets created
        global ani_ref_obj
        ani_ref_obj = animation.FuncAnimation(fig, animate, interval=200, fargs=(self.table,))


class DataTableFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # initialize data table to display information
        cols = ('Methane [ppb]','Battery [V]', 'Status')
        self.table = ttk.Treeview(self, columns=cols, show='headings', height=len(namelist))
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 50))
        style.configure("Treeview", rowheight=60, font=(None, 60))
        self.table.column("Methane [ppb]", minwidth=0, width=650, stretch=False, anchor=tk.CENTER)
        self.table.column("Battery [V]", minwidth=0, width=650, stretch=False, anchor=tk.CENTER)
        self.table.column("Status", minwidth=0, width=650, stretch=False, anchor=tk.CENTER)

        for col in cols:
            self.table.heading(col, text=col)

        self.table.grid(row=1, column=0, columnspan=2)
        shared = get_data()

        self.table.insert('', 'end', "values", values=(shared.get("Methane"),
                                                       shared.get("Battery"),
                                                       shared.get("Status")))

        #for index in range (0, len(varlist)):
            #self.table.insert('','end', varlist[index],values=(namelist[index],shared.get(varlist[index])))

        self.table.pack()

    def get_table(self):
        return self.table


class GraphFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # initialize canvas for plotting
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()#fill=tk.BOTH)#, expand=True)


app = MethaneGUIApp()
app.mainloop()
