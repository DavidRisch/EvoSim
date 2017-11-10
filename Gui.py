from Tkinter import *
import Tkinter

root = Tkinter.Tk()
root.geometry("400x400+10+10")
button = Tkinter.Button(root, text="Y+", fg="black",
                        command=YP, repeatinterval=1, repeatdelay=1)
button.pack()
button.place(x=75, y=25, width=50, height=50)

button = Tkinter.Button(root, text="X-", fg="black",
                        command=XN, repeatinterval=1, repeatdelay=1)
button.pack()
button.place(x=25, y=75, width=50, height=50)

button = Tkinter.Button(root, text="X+", fg="black",
                        command=XP, repeatinterval=1, repeatdelay=1)
button.pack()
button.place(x=125, y=75, width=50, height=50)

button = Tkinter.Button(root, text="Y-", fg="black",
                        command=YN, repeatinterval=1, repeatdelay=1)
button.pack()
button.place(x=75, y=125, width=50, height=50)

button = Tkinter.Button(root, text="Z+", fg="black",
                        command=ZP, repeatinterval=1, repeatdelay=1)
button.pack()
button.place(x=185, y=50, width=50, height=50)

button = Tkinter.Button(root, text="Z-", fg="black",
                        command=ZN, repeatinterval=1, repeatdelay=1)
button.pack()
button.place(x=185, y=100, width=50, height=50)
############################
cxtxt = StringVar()
cytxt = StringVar()
cztxt = StringVar()
cxtxt.set("X:0")
cytxt.set("Y:0")
cztxt.set("Z:0")

butx = Tkinter.Button(root, textvariable=cxtxt, fg="black",
                      command=0, repeatinterval=1, repeatdelay=1)
butx.pack()
butx.place(x=245, y=25, width=125, height=50)

buty = Tkinter.Button(root, textvariable=cytxt, fg="black",
                      command=0, repeatinterval=1, repeatdelay=1)
buty.pack()
buty.place(x=245, y=75, width=125, height=50)

butz = Tkinter.Button(root, textvariable=cztxt, fg="black",
                      command=0, repeatinterval=1, repeatdelay=1)
butz.pack()
butz.place(x=245, y=125, width=125, height=50)
##########################
butopen = Tkinter.Button(root, text="Open", fg="black",
                         command=read, repeatinterval=1, repeatdelay=1)
butopen.pack()
butopen.place(x=25, y=195, width=125, height=50)

root.mainloop()





