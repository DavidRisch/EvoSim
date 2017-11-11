from tkinter import *
import tkinter
from PIL import Image
from PIL import ImageTk
import random
import math
import time
from agent import Agent


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
    global tick_count

    position = [random.uniform(0, configuration["Area"]), random.uniform(0, configuration["Area"])]
    direction = random.uniform(0, 1)
    agent = Agent(position, direction, tick_count, configuration)

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
