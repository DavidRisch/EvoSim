from tkinter import *
import tkinter
from PIL import Image
from PIL import ImageTk
import random
import math
import time


# pip install pillow

configuration = {
    "Agent_Health": 100,
    "Agent_MaxSpeed": 0.1,
    "Agent_NaturalDecay": 0.4,
    "Agent_MinPopulation": 15,
    "Food_Value": 30,
    "Food_Diameter" : 0.5,
    "Area": 15,
}

agents = []
food_positions = []
highlighted_agent = None
tick_count = 0

area_in_px = 800
one_unit_in_px = 0
agent_images = []
images = {}

speed = 20  # ticks/second
speed_before_pause = None


class Agent:
    position = []
    direction = None
    health = None
    birth = None

    def __init__(self, position, direction):
        print("NewAgent")
        self.position = position
        self.direction = direction
        self.health = configuration["Agent_Health"]
        self.birth = tick_count

    def tick(self):
        # Movement
        angle = self.direction * 2 * math.pi

        self.position[0] += math.sin(angle) * configuration["Agent_MaxSpeed"]
        self.position[1] += math.cos(angle) * configuration["Agent_MaxSpeed"]

        self.position = wrap_position(self.position)

        # NaturalDecay
        self.health -= configuration["Agent_NaturalDecay"]

    def eat(self):
        self.health += configuration["Food_Value"]

    def die(self):
        agents.remove(self)

    def get_distance(self, position):
        distance_x = self.position[0] - position[0]
        distance_y = self.position[1] - position[1]
        distance = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))
        return distance

    def get_information_string(self):
        string = "Position: [" + str(round(self.position[0], 2)) + ", " + str(round(self.position[1], 2)) + "]\n"
        string += "Health: " + str(round(self.health, 2)) + "\n"
        string += "Age: " + str(tick_count - self.birth) + "\n"

        return string


def tick():
    global tick_count

    start_ms = time.time()*1000.0

    if speed != 0:
        tick_count += 1

        fill_to_mim_population()

        for agent in agents:
            agent.tick()

    draw_frame()

    if speed != 0:
        current_ms = time.time()*1000.0
        time_to_next_tick = round((1/speed)*1000 - (current_ms - start_ms))
    else:
        time_to_next_tick = round((1/20)*1000)  # 25fps
    tkinter_root.after(time_to_next_tick, tick)


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
    fill_to_mim_population()
    draw_frame()


def fill_to_mim_population():
    while len(agents) < configuration["Agent_MinPopulation"]:
        add_agent()


def add_food():
    global food_positions
    position = [random.uniform(0, configuration["Area"]), random.uniform(0, configuration["Area"])]
    food_positions.append(position)


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

    for position in food_positions:
        draw_food(position)

    string = "Tick: " + str(tick_count) + "\n"
    string += "Agents: " + str(len(agents)) + " / " + str(configuration["Agent_MinPopulation"])
    general_information_text.set(string)

    if highlighted_agent is not None:
        agent_information_text.set(highlighted_agent.get_information_string())


def draw_agent(agent):
    image_index = round(agent.direction*60)
    if image_index == 60:
        image_index = 0
    image = agent_images[image_index]

    center_x = agent.position[0] * one_unit_in_px
    center_y = area_in_px - agent.position[1] * one_unit_in_px

    tkinter_root.canvas.create_image(center_x, center_y, anchor=CENTER, image=image)

    if agent == highlighted_agent:
        tkinter_root.canvas.create_image(center_x, center_y, anchor=CENTER, image=images["Highlight"])


def draw_food(position):
    tkinter_root.canvas.create_image(position[0] * one_unit_in_px,
                                     area_in_px - position[1] * one_unit_in_px,
                                     anchor=CENTER, image=images["Food"])


def prepare_canvas():
    global one_unit_in_px
    global agent_images
    global images

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

    image = Image.open("graphics/Food.png")
    size = round(one_unit_in_px * configuration["Food_Diameter"])
    image = image.resize((size, size), Image.ANTIALIAS)
    images["Food"] = ImageTk.PhotoImage(image)

    image = Image.open("graphics/Highlight.png")
    size = round(one_unit_in_px * 0.5)
    image = image.resize((size, size), Image.ANTIALIAS)
    images["Highlight"] = ImageTk.PhotoImage(image)


def click_on_canvas(event):
    global highlighted_agent

    position = [event.x, area_in_px - event.y]
    for i in [0, 1]:
        position[i] = position[i] / one_unit_in_px

    closest_distance = 9999999999
    closest_agent = None

    for agent in agents:
        distance = agent.get_distance(position)
        if distance < closest_distance:
            closest_distance = distance
            closest_agent = agent

    highlighted_agent = closest_agent


def toggle_pause(event=None):
    global speed
    global speed_before_pause

    if speed != 0:
        speed_before_pause = speed
        speed = event.x  # suppress error (unused value)
        speed = 0
    else:
        speed = speed_before_pause


window_width = 5 + area_in_px + 5
window_height = 5 + 25 + 5 + area_in_px + 5 + 50 + 5

tkinter_root = tkinter.Tk()
tkinter_root.geometry(str(window_width)+"x"+str(window_height)+"+10+10")

button = tkinter.Button(tkinter_root, text="Reset", fg="black",
                        command=reset)
button.pack()
button.place(x=5, y=5, width=60, height=25)


label_y = 5 + 25 + 5 + area_in_px + 5
label_width = (window_width/2 - 10)

agent_information_text = StringVar()
agent_information_text.set("")
agent_information = Label(tkinter_root, anchor=NW, justify=LEFT, textvariable=agent_information_text)
agent_information.pack()

agent_information.place(x=(window_width/2 + 5), y=label_y, width=label_width, height=50)

general_information_text = StringVar()
general_information_text.set("")
general_information = Label(tkinter_root, anchor=NW, justify=LEFT, textvariable=general_information_text)
general_information.pack()

general_information.place(x=5, y=label_y, width=label_width, height=50)

prepare_canvas()

tkinter_root.canvas.bind("<Button-1>", click_on_canvas)
tkinter_root.bind("<space>", toggle_pause)

reset()
tkinter_root.after(500, tick)
tkinter_root.mainloop()
