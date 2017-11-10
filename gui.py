from tkinter import *
import tkinter
#import numpy as np

Configuration = {
    "Agent_Health" : 100,
    "Agent_MaxHealth" : 1000,
    "Agent_NaturalDecay" : 3,
    "Agent_MinNumber" : 3,
    "Food_Value" : 30,
    "Area_X" : 100,
    "Area_y" : 100
}

agents = []


class Agent:
    position = []
    health = 0

    def __init__(self, position):
        print("NewAgent:" + str(position[0]))
        self.position = position



def reset():
    print("########Reset########")
    global agents
    agents = []
    add_agent()

def add_agent():
    global agents

    position = [50, 50]
    agent = Agent(position)

    agents.append(agent)


root = tkinter.Tk()


root.geometry("400x400+10+10")
button = tkinter.Button(root, text="Reset", fg="black",
                        command=reset)
button.pack()
button.place(x=5, y=5, width=60, height=25)


root.mainloop()





