import threading
import time
from tkinter import *
from tkinter import ttk
from threading import Timer
import tkinter as tk
from PIL import Image, ImageTk
from itertools import count, cycle
import os
import brain_flow2 as bf

wait = True
frames = []
delay = 100
index = 0
size = 0
loops = 0
check = True
im = []
rotation_list = (0, 1, 2, 3, 4)
img_list = []
start_time = 0
direction = ""
trial_count = 0
lbl = None
start_button = None
win = None
photo = None
label = None

number_of_trials = 10



def load_frame(im):
    global lbl, win, rotation_list, start_time, direction, photo, label


    if rotation_list[index] == 0:
        lbl.grid(row=0, column=1)
        direction = 'forward'
    elif rotation_list[index] == 1:
        lbl.grid(row=1, column=3, sticky='e')
        direction = 'right'
    elif rotation_list[index] == 2:
        lbl.grid(row=2, column=1, sticky='s')
        direction = 'backward'
    elif rotation_list[index] == 3:
        lbl.grid(row=1, column=0, sticky='w')
        direction = 'left'
    else:
        lbl.grid(row=1, column=1,sticky='nsew')
        direction = 'stop'

    start_button.destroy()

    if isinstance(im, str):
        img = Image.open(im)
        img2 = Image.open(im)
    frame = []


    try:
        for i in count(1):
            frame.append(ImageTk.PhotoImage(img.copy().resize((600, 300))))
            img.seek(i)

    except EOFError:
        pass

    frame_size = len(frame)
    frames_cycle = cycle(frame)
    # self.frames = frames

    try:
        delay = img.info['duration']
    except:
        delay = 100

    if len(frame) == 1:
        lbl.config(image=img2)

    else:
        wait = True
        print(im)
        start_time = time.time()
        bf.empty_buffer()

        next_frame(0, frame_size, frames_cycle)


def unload():
    global index, img_list , lbl, checker, direction, trial_count, win, number_of_trials
    print(number_of_trials)

    bf.get_data(direction)
    lbl.config(image=None)
    print("h")


    if index == len(img_list)-1:
        trial_count += 1
        index = 0
    else:
        index += 1

    #After 10 trials, close the window
    if trial_count >= number_of_trials:
        win.destroy()
        return


    img = img_list[index]
    lbl.config(image="")

    win.after(1000, lambda: load_frame(img))


def next_frame(loop_count,frame_size,frames_cycle):
    global img_list,myFrame

    loop_count += 1
    end = time.time()

    if int(end-start_time) >= 5:
        print("unload")
        unload()

    elif frames_cycle:
        lbl.config(image=next(frames_cycle))
        win.after(100, lambda: next_frame(loop_count, frame_size, frames_cycle))

def start_data_obtain_session(num_trial):
    global lbl, start_button, win, number_of_trials, photo, label, number_of_trials
    number_of_trials = int(num_trial)
    print(num_trial)
    print(number_of_trials)
    print(number_of_trials)
    print(number_of_trials)
    print(number_of_trials)
    print(number_of_trials)


    for i in os.listdir("gesture_images"):
        path = str('gesture_images/' + i)
        img_list.append(path)

    win = tk.Tk()
    win.geometry("800x800")

    for i in range(3):
        win.columnconfigure(i, weight=1)

    win.rowconfigure(1, weight=1)
    lbl = tk.Label(win)
    start_button = tk.Button(win, height=5, width=20, text="START", command=lambda: load_frame(img_list[0]))

    print("xxxxx")
    start_button.grid(row=1, column=1)

    bf.start_connection()

    win.mainloop()


#start_data_obtain_session()


