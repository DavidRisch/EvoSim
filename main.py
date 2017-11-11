from tkinter import *
import tkinter
from PIL import Image
from PIL import ImageTk
import random
import math
import time


# pip install pillow

configuration = {
    "Area": 15,
    "Agent_Health": 100,
    "Agent_MaxMovementSpeed": 0.1,
    "Agent_MaxTurningSpeed": 0.02,
    "Agent_NaturalDecay": 0.1,
    "Agent_MinPopulation": 15,
    "Food_Value": 30,
    "Food_Diameter": 0.5,
    "Food_PerTick": 0.1,
    "Sensor_Food_Range": 5,
    "Sensor_Food_Middle_Angel": 30,
    "Sensor_Food_Side_Angel": 30,
}

agents = []
food_positions = []
highlighted_agent = None
tick_count = 0
food_to_spawn = 0  # configuration["Food_PerTick"] is not an int

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
    input = []
    output = [0.1, 0.8]   # temp

    def __init__(self, position, direction):
        # print("NewAgent")
        self.position = position
        self.direction = direction
        self.health = configuration["Agent_Health"]
        self.birth = tick_count

    def tick(self):
        self.input = [0, 0, 0]

        # Food
        for position in food_positions:
            distance = self.get_distance(position)
            if distance < 0.5 + configuration["Food_Diameter"] / 2:
                food_positions.remove(position)
                self.eat()
            elif distance < configuration["Sensor_Food_Range"]:
                agent_to_food_x = position[0] - self.position[0]
                agent_to_food_y = position[1] - self.position[1]

                angle = (math.atan2(-agent_to_food_x, -agent_to_food_y) + math.pi) / 2

                direction = angle / math.pi
                direction = direction - self.direction
                if direction < 0:
                    direction = 1 + direction

                size_middle = configuration["Sensor_Food_Middle_Angel"]/360
                size_side = configuration["Sensor_Food_Side_Angel"]/360
                if (1 - size_middle/2 - size_side) < direction < (1 - size_middle/2):
                    self.input[0] += (configuration["Sensor_Food_Range"] - distance) / configuration["Sensor_Food_Range"]
                elif direction < size_middle/2 or direction > (1 - size_middle/2):
                    self.input[1] += (configuration["Sensor_Food_Range"] - distance) / configuration["Sensor_Food_Range"]
                elif size_middle/2 < direction < size_middle/2 + size_side:
                    self.input[2] += (configuration["Sensor_Food_Range"] - distance) / configuration["Sensor_Food_Range"]

        # Neural Network

        # self.input    float[3]     x >= 0
        # self.output   float[2]
        #
        #
        #
        #
        #

        for i in range(0, len(self.output)):
            self.output[i] = confine_number(self.output[i], -1, 1)

        # Movement
        self.direction += self.output[0] * configuration["Agent_MaxTurningSpeed"]
        self.direction = wrap_direction(self.direction)

        angle = self.direction * 2 * math.pi

        self.position[0] += math.sin(angle) * self.output[1] * configuration["Agent_MaxMovementSpeed"]
        self.position[1] += math.cos(angle) * self.output[1] * configuration["Agent_MaxMovementSpeed"]

        self.position = wrap_position(self.position)

        # NaturalDecay
        self.health -= configuration["Agent_NaturalDecay"]

        # Die
        if self.health <= 0:
            self.die()

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
        string = "Input: [" + ", ".join(str(e) for e in self.input) + "]\n"
        string += "Position: [" + str(round(self.position[0], 2)) + ", " + str(round(self.position[1], 2)) + "]\n"
        string += "Health: " + str(round(self.health, 2)) + "\n"
        string += "Age: " + str(tick_count - self.birth) + "\n"

        return string


def tick():
    global tick_count
    global food_to_spawn

    start_ms = time.time()*1000.0

    if speed != 0:
        tick_count += 1

        fill_to_min_population()

        for agent in agents:
            agent.tick()

        food_to_spawn += configuration["Food_PerTick"]
        while food_to_spawn >= 1:
            food_to_spawn -= 1
            add_food()

    draw_frame()

    if speed != 0:
        current_ms = time.time()*1000.0
        time_to_next_tick = round((1/speed)*1000 - (current_ms - start_ms))
    else:
        time_to_next_tick = round((1/20)*1000)  # 25fps

    if time_to_next_tick < 2:
        time_to_next_tick = 2
    tkinter_root.after(time_to_next_tick, tick)


def wrap_position(position):
    for i in [0, 1]:
        if position[i] < 0:
            position[i] = configuration["Area"] + position[i]
        if position[i] > configuration["Area"]:
            position[i] = configuration["Area"] - position[i]

    return position


def wrap_direction(direction):
    if direction < 0:
        direction = 1 + direction
    if direction > 1:
        direction = 1 - direction

    return direction


def confine_number(number, minimum, maximum):
    if number < minimum:
        number = minimum
    elif number > maximum:
        number = maximum

    return number


def start():
    print("########Start########")
    global agents
    agents = []
    fill_to_min_population()
    draw_frame()


def fill_to_min_population():
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
    tkinter_root.canvas.place(x=5, y=70, width=area_in_px, height=area_in_px)

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
        speed = event.type  # suppress error (unused value)
        speed = 0
    else:
        speed = speed_before_pause

    speed_slider.set(speed)


def set_speed(value):
    global speed
    speed = int(value)


window_width = 5 + area_in_px + 5
window_height = 5 + 60 + 5 + area_in_px + 5 + 100 + 5

tkinter_root = tkinter.Tk()
tkinter_root.geometry(str(window_width)+"x"+str(window_height)+"+10+10")

# button = tkinter.Button(tkinter_root, text="Reset", fg="black", command=reset)
# button.pack()
# button.place(x=5, y=5, width=60, height=25)

speed_slider = Scale(tkinter_root, from_=0, to=800, orient=HORIZONTAL, command=set_speed)
speed_slider.pack()
speed_slider.place(x=(window_width - 405), y=5, width=400, height=65)
speed_slider.set(speed)

label_y = 5 + 60 + 5 + area_in_px + 5
label_width = (window_width/2 - 10)

agent_information_text = StringVar()
agent_information_text.set("")
agent_information = Label(tkinter_root, anchor=NW, justify=LEFT, textvariable=agent_information_text)
agent_information.pack()

agent_information.place(x=(window_width/2 + 5), y=label_y, width=label_width, height=100)

general_information_text = StringVar()
general_information_text.set("")
general_information = Label(tkinter_root, anchor=NW, justify=LEFT, textvariable=general_information_text)
general_information.pack()

general_information.place(x=5, y=label_y, width=label_width, height=100)

prepare_canvas()

tkinter_root.canvas.bind("<Button-1>", click_on_canvas)
tkinter_root.bind("<space>", toggle_pause)

start()
tkinter_root.after(500, tick)
tkinter_root.mainloop()
