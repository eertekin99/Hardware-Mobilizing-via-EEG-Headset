import automatic_data_obtain as do
import direction_classifier as dc
import threading
import time
from tkinter import *
from tkinter import ttk
from threading import Timer
import tkinter as tk
from PIL import Image, ImageTk
from itertools import count, cycle
import os

win = None
win1 = None
number_of_trials = None
algorithm = None

def option_screen():
    global win, number_of_trials

    def goOut():
        win.destroy()

    win = tk.Tk()
    win.geometry("800x800")
    lbl = tk.Label(win)

    win.configure(background='#5d90ad')
    start_button = tk.Button(win, height=5, width=20, text="NEXT", command=lambda: goOut())
    start_button.pack(side='top', pady=(10, 0))

    # Change number_of_trials with radiobuttons
    number_of_trials = StringVar(win, 10)


    # Dictionary to create multiple buttons
    values = {  "10 (~5 min)": 10,
                "15 (~7.5 min)": 15,
                "20 (~10 min)": 20
              }

    # Loop is used to create multiple Radio buttons
    # rather than creating each button separately
    for (text, value) in values.items():
        Radiobutton(win, text=text, variable=number_of_trials,
                    value=value, indicator=0,
                    background="light blue").pack(ipady=10)

    def resize_image(event):
        new_width = event.width
        new_height = event.height
        image = copy_of_image.resize((new_width, new_height))
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo  # avoid garbage collection

    image = Image.open('brain.jpg')
    copy_of_image = image.copy()
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(win, image=photo)
    label.bind('<Configure>', resize_image)
    label.pack(fill=BOTH, expand=YES)

    win.mainloop()

def algorithm_option_screen():
    global win1, algorithm

    def goOut():
        win1.destroy()

    win1 = tk.Tk()
    win1.geometry("800x800")
    lbl = tk.Label(win1)

    win1.configure(background='#5d90ad')
    start_button = tk.Button(win1, height=5, width=20, text="NEXT", command=lambda: goOut())
    start_button.pack(side='top', pady=(10, 0))

    # Change number_of_trials with radiobuttons
    algorithm = StringVar(win1, "SVM")


    # Dictionary to create multiple buttons
    values = {  "SupportVectorMachines": "SVM",
                "LogisticRegression": "LR",
                "LinearDiscriminantAnalysis": "LDA",
                "RandomForestClassifier": "RFC",
                "GradientBoostingClassifier": "XGB",
                "MultinomialNB": "MNB",
                "DecisionTreeClassifier": "DTC",
                "KNeighborsClassifier": "KNN",
                "VotingClassifier": "VC"
              }

    # Loop is used to create multiple Radio buttons
    # rather than creating each button separately
    for (text, value) in values.items():
        Radiobutton(win1, text=text, variable=algorithm,
                    value=value, indicator=0,
                    background="light blue").pack(ipady=10)

    def resize_image(event):
        new_width = event.width
        new_height = event.height
        image = copy_of_image.resize((new_width, new_height))
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo  # avoid garbage collection

    image = Image.open('brain.jpg')
    copy_of_image = image.copy()
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(win1, image=photo)
    label.bind('<Configure>', resize_image)
    label.pack(fill=BOTH, expand=YES)

    win1.mainloop()

#option_screen()
#num_trial = int(number_of_trials.get())
#do.start_data_obtain_session(num_trial)
#import preprocessing_modeling
algorithm_option_screen()
file = "SVM" #Default
file = str(algorithm.get()) + ".sav"
print(file)
dc.main(file)
