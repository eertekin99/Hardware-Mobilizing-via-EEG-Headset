'''---------------Import libraries-------------------'''
import tkinter as tk
from itertools import count, cycle
from PIL import Image, ImageTk

'''--------------global variables----------------'''
framelist = []      # List to hold all the frames
frame_index = 0
counter = 0
anim = None
list_gif_frames =[]

'''-----------------methods---------------------'''
def animate_gif(counter):
    global anim
    l1.config(image = framelist[counter])
    counter +=1
    if counter > len(framelist)-1:
        counter = 0
    #recall animate_gif method
    anim = window.after(100, lambda :animate_gif(counter))
def cancel_gif():
    window.after_cancel(anim)
    window.config(image=None)
    l1.config(image=None)

def stop_gif():
    global anim
    #stop recall method
    window.after_cancel(anim)

'''-------------Tkinter GUI main window----------------------'''
window = tk.Tk()
window.title("GIF LOADED")
window.geometry("800x800")
'''--------------count all frames in gif and saved in a list-----------------'''

im = 'images/hand-ball-goal.gif'
img = Image.open(str(im))
# frame = []
try:
    for i in count(1):
        framelist.append(ImageTk.PhotoImage(img.copy()))
        img.seek(i)
except EOFError:
    pass
# last_frame =
'''------------label to show gif--------------------'''
l1 = tk.Label(window, bg='#202020', image = "")
l1.pack()
'''-----------------button to start gif--------------------'''
b1 = tk.Button(window, text = "start", command = lambda :animate_gif(0))
b1.pack()
'''---------------button to stop gif---------------------------'''
b2 = tk.Button(window, text = "stop", command = stop_gif)
b2.pack()
b3 = tk.Button(window, text = "nxt", command =  lambda :animate_gif(0))
b3.pack()
b4 = tk.Button(window, text = "cancel", command =  lambda :cancel_gif())
b4.pack()

window.mainloop()