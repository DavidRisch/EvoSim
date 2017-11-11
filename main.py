from tkinter import *
import tkinter
from PIL import Image
from PIL import ImageTk
import random
import math


# pip install pillow

configuration = {
    "Agent_Health": 100,
    "Agent_MaxHealth": 1000,
    "Agent_MaxSpeed": 0.1,
    "Agent_NaturalDecay": 3,
    "Agent_MinPopulation": 15,
    "Food_Value": 30,
    "Area": 15,
}

agents = []
fps = 20


class Agent:
    position = []
    direction = 0
    health = 0

    def __init__(self, position, direction):
        print("NewAgent")
        self.position = position
        self.direction = direction


def tick():
    # print("tick")

    for agent in agents:
        angle = agent.direction * 2 * math.pi

        agent.position[0] += math.sin(angle) * configuration["Agent_MaxSpeed"]
        agent.position[1] += math.cos(angle) * configuration["Agent_MaxSpeed"]

        agent.position = wrap_position(agent.position)

    draw_frame()
    tkinter_root.after(round((1/fps)*1000), tick)


def wrap_position(position):
    for i in [0, 1]:
        if position[i] < 0:
            position[i] = configuration["Area"] + position[i]
        if position[i] > configuration["Area"]:
            position[i] = configuration["Area"] - position[i]

    return position


def reset():
    print("########Reset########")
    global agents
    agents = []
    fill_to_min_population()
    draw_frame()


def fill_to_min_population():
    while len(agents) < configuration["Agent_MinPopulation"]:
        add_agent()


def add_agent():
    global agents

    position = [random.uniform(0, configuration["Area"]), random.uniform(0, configuration["Area"])]
    direction = random.uniform(0, 1)
    agent = Agent(position, direction)
    print(direction)

    agents.append(agent)


def draw_frame():
    tkinter_root.canvas.delete("all")
    for agent in agents:
        draw_agent(agent)


def draw_agent(agent):
    image_index = round(agent.direction*60)
    if image_index == 60:
        image_index = 0
    image = agent_images[image_index]
    tkinter_root.canvas.create_image(agent.position[0] * one_unit_in_px,
                                     area_in_px - agent.position[1] * one_unit_in_px,
                                     anchor=CENTER, image=image)


agent_images = []


def prepare_canvas():
    global one_unit_in_px
    global agent_images

    one_unit_in_px = area_in_px/configuration["Area"]
    one_unit_in_px = round(one_unit_in_px)

    tkinter_root.canvas = Canvas(tkinter_root, width=1, height=1, bg="#eeeeee")
    tkinter_root.canvas.configure(highlightthickness=0, borderwidth=0)
    tkinter_root.canvas.place(x=5, y=40, width=area_in_px, height=area_in_px)

    agent_image = Image.open("graphics/Agent.png")
    for i in range(0, 60):
        image = agent_image
        image = image.rotate(-(i / 60) * 360)
        image = image.resize((one_unit_in_px, one_unit_in_px), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)

        agent_images.append(image)


area_in_px = 800
one_unit_in_px = 0

tkinter_root = tkinter.Tk()
tkinter_root.geometry("810x845+10+10")
button = tkinter.Button(tkinter_root, text="Reset", fg="black",
                        command=reset)
button.pack()
button.place(x=5, y=5, width=60, height=25)


prepare_canvas()

reset()
tkinter_root.after(500, tick)
tkinter_root.mainloop()
