from agent import Agent
from gui import Gui
import saveload

import random
import time
import math

configuration = {
    "Area": 15,
    "Agent_Health": 100,
    "Agent_MaxMovementSpeed": 0.1,
    "Agent_MaxTurningSpeed": 0.02,
    "Agent_NaturalDecay": 0.7,
    "Agent_MinPopulation": 10,
    "Food_Value": 10,
    "Food_Diameter": 0.5,
    "Food_PerTick": 0.06,
    "Sensor_Food_Range": 3.5,
    "Sensor_Food_Middle_Angel": 30,
    "Sensor_Food_Side_Angel": 30,
}

agents = []
food_positions = []
tick_count = 0
food_to_spawn = 0  # keeps track of food, that needs to be spawned (because configuration["Food_PerTick"] is not an int)

fps = 20
last_frame_ms = 0
speed = 20  # ticks/second
speed_before_pause = 0

gui = None


def tick():
    global gui
    global tick_count
    global food_to_spawn
    global last_frame_ms

    start_ms = time.time()*1000.0

    if speed != 0:
        tick_count += 1

        fill_to_min_population()

        for agent in agents:
                sensors = [0, 0, 0]

                # Food
                for position in food_positions:
                    distance = agent.get_distance(position)
                    if distance < 0.5 + configuration["Food_Diameter"] / 2:
                        food_positions.remove(position)
                        agent.eat()
                    elif distance < configuration["Sensor_Food_Range"]:

                        sensors = calculate_sensors(agent, position, distance, sensors)

                agent.sensors = sensors  # for agent.get_information_string

                # Neural Network
                agent.react(sensors)
                output = agent.output

                # for i in range(0, len(output)):
                # output[i] = confine_number(2*output[i]-1, -1, 1)
                output[0] = 2 * output[0] - 1

                # Movement
                agent.direction += output[0] * configuration["Agent_MaxTurningSpeed"]
                agent.direction = wrap_direction(agent.direction)

                angle = agent.direction * 2 * math.pi

                agent.position[0] += math.sin(angle) * output[1] * configuration["Agent_MaxMovementSpeed"]
                agent.position[1] += math.cos(angle) * output[1] * configuration["Agent_MaxMovementSpeed"]

                agent.position = wrap_position(agent.position)

                # NaturalDecay
                agent.health -= configuration["Agent_NaturalDecay"]

                # Die
                if agent.health <= 0:
                    agents.remove(agent)

        food_to_spawn += configuration["Food_PerTick"]
        while food_to_spawn >= 1:
            food_to_spawn -= 1
            add_food()

    current_ms = time.time() * 1000.0

    if current_ms >= last_frame_ms + round((1/fps)*1000):
        last_frame_ms = current_ms
        gui.draw_frame(agents, food_positions, tick_count)

    if speed != 0:
        time_to_next_tick = round((1/speed)*1000 - (current_ms - start_ms))
    else:
        time_to_next_tick = round((1/20)*1000)  # 25fps

    if time_to_next_tick < 2:
        time_to_next_tick = 1

    gui.tkinter_root.after(time_to_next_tick, tick)


def test_position(event):
    agents[0].highlighted = True
    food_position = [event.x, gui.area_in_px - event.y]
    for i in [0, 1]:
        food_position[i] = food_position[i] / gui.one_unit_in_px

    distance = agents[0].get_distance(food_position)

    print(calculate_sensors(agents[0], food_position, distance, [0, 0, 0]))


def calculate_sensors(agent, food_position, distance, old_sensors):
    sensors = [0, 0, 0]

    direction = calculate_direction_difference(agent.position, food_position, agent.direction)

    size_middle = configuration["Sensor_Food_Middle_Angel"] / 360
    size_side = configuration["Sensor_Food_Side_Angel"] / 360
    if (1 - size_middle / 2 - size_side) < direction < (1 - size_middle / 2):
        sensors[0] = (configuration["Sensor_Food_Range"] - distance) / configuration[
            "Sensor_Food_Range"]
    elif direction < size_middle / 2 or direction > (1 - size_middle / 2):
        sensors[1] = (configuration["Sensor_Food_Range"] - distance) / configuration[
            "Sensor_Food_Range"]
    elif size_middle / 2 < direction < size_middle / 2 + size_side:
        sensors[2] = (configuration["Sensor_Food_Range"] - distance) / configuration[
            "Sensor_Food_Range"]

    for i in range(0, len(sensors)):
        sensors[i] = old_sensors[i] + confine_number(sensors[i], 0, None)

    return sensors


def calculate_direction_difference(position_a, position_b, direction_a):
    a_to_b_x = position_b[0] - position_a[0]
    a_to_b_y = position_b[1] - position_a[1]

    angle = (math.atan2(-a_to_b_y, -a_to_b_x) + math.pi) / 2

    direction = angle / math.pi
    direction = -direction + 0.25

    direction = direction - direction_a
    while direction < 0:
        direction = 1 + direction

    return direction


def confine_number(number, minimum, maximum):
    if minimum is not None:
        if number < minimum:
            number = minimum

    if maximum is not None:
        if number > maximum:
            number = maximum

    return number


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


def start():
    global gui
    global agents

    print("########Start########")

    gui = Gui(configuration)

    gui.tkinter_root.button_save.bind("<Button-1>", save)
    gui.tkinter_root.button_load.bind("<Button-1>", load)
    gui.tkinter_root.speed_slider.bind("<B1-Motion>", set_speed)
    gui.tkinter_root.speed_slider.bind("<Button-1>", set_speed)
    gui.tkinter_root.speed_slider.bind("<ButtonRelease-1>", set_speed)
    gui.tkinter_root.speed_slider.set(speed)

    # gui.tkinter_root.canvas.bind("<Button-1>", click_on_canvas)
    gui.tkinter_root.canvas.bind("<Button-1>", lambda event: gui.click_on_canvas(event, agents))
    gui.tkinter_root.bind("<space>", toggle_pause)

    # gui.tkinter_root.canvas.bind("<Button-1>", test_position)

    agents = []
    fill_to_min_population()
    gui.draw_frame(agents, food_positions, tick_count)

    gui.tkinter_root.after(500, tick)
    gui.tkinter_root.mainloop()


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


# noinspection PyUnusedLocal
def toggle_pause(event):
    global speed
    global speed_before_pause

    if speed != 0:
        speed_before_pause = speed
        speed = 0
        gui.draw_frame(agents, food_positions, tick_count)
    else:
        speed = speed_before_pause

    gui.tkinter_root.speed_slider.set(speed)


# noinspection PyUnusedLocal
def set_speed(event):
    global speed
    global gui

    speed = int(gui.tkinter_root.speed_slider.get())


# noinspection PyUnusedLocal
def save(event):
    print("Saving...")
    agents_data = []
    for agent in agents:
        agent_data = {
            "position": agent.position,
            "direction": agent.direction,
            "health": agent.health,
        }
        agents_data.append(agent_data)

    data = {
        "agent_data": agents_data,
        "configuration": configuration,
        "food_positions": food_positions,
    }
    print(data)
    saveload.save(data)


# noinspection PyUnusedLocal
def load(event):
    print("Loading...")


start()
