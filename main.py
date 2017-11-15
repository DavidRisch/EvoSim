from agent import Agent
from gui import Gui
import saveload

import random
import time
import math
import threading

configuration = {
    "Area": 40,
    "Agent_Health": 100,
    "Agent_MaxMovementSpeed": 0.1,
    "Agent_MaxTurningSpeed": 0.02,
    "Agent_NaturalDecay": 0.1,
    "Agent_MinPopulation": 8,
    "Food_Value": 50,
    "Food_Diameter": 0.5,
    "Food_PerTick": 0.035,
    "Sensor_Food_Range": 8,
    "Sensor_Food_Middle_Angel": 30,
    "Sensor_Food_Side_Angel": 30,
}

agents = []
food_positions = []
tick_count = 0
food_to_spawn = 0  # keeps track of food, that needs to be spawned (because configuration["Food_PerTick"] is not an int)


fps = 20
fps_table = 5
last_frame_ms = 0
last_table_frame_ms = 0
speed = 20  # ticks/second
speed_before_pause = 0
wait_ever_x_ticks = 25  # prevent program from freezing
number_of_threads = 4

mark_agents_at_tick = 2000

gui = None


thread_tick_tasks = []
exit_tasks = False


class TickThread (threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def run(self):
        print("Starting " + self.name)
        while not exit_tasks:
            if thread_tick_tasks[self.thread_id] is not None:
                for agent in list(thread_tick_tasks[self.thread_id]):
                    if agent is not None:
                        tick_agent(agent)

                thread_tick_tasks[self.thread_id] = None

            time.sleep(0.0001)  # 0.1ms
        print("Exiting " + self.name)


def loop():
    global last_frame_ms
    global last_table_frame_ms

    start_ms = time.time() * 1000.0

    if speed != 0:
        tick()

    current_ms = time.time() * 1000.0

    if current_ms >= last_frame_ms + round((1/fps)*1000):
        last_frame_ms = current_ms
        gui.draw_frame(agents, food_positions, tick_count)

    if current_ms >= last_table_frame_ms + round((1 / fps_table) * 1000):
        last_table_frame_ms = current_ms
        gui.update_table(agents, tick_count)

    if speed != 0:
        time_to_next_tick = round((1/speed)*1000 - (current_ms - start_ms))
    else:
        time_to_next_tick = round((1/20)*1000)  # 25fps

    if time_to_next_tick <= 1 and tick_count % wait_ever_x_ticks == 0:
        time_to_next_tick = 1

    gui.tkinter_root.after(time_to_next_tick, loop)


def tick():
    global tick_count
    global food_to_spawn

    tick_count += 1

    fill_to_min_population()

    size = math.floor(len(agents) / number_of_threads)

    for i in range(0, number_of_threads-1):
        thread_tick_tasks[i] = agents[size*i:(size*(i+1))]

    thread_tick_tasks[number_of_threads - 1] = agents[(size * (number_of_threads - 1)):]

    tasks_complete = False
    while not tasks_complete:
        time.sleep(0.0001)  # 0.1ms
        tasks_complete = True
        for tick_tasks in thread_tick_tasks:
            if tick_tasks is not None:
                tasks_complete = False

    for agent in agents:
        agent.direction += agent.direction_change
        agent.direction = wrap_direction(agent.direction)
        agent.position[0] += agent.position_change_x
        agent.position[1] += agent.position_change_y
        agent.position = wrap_position(agent.position)

    for agent in agents:
        if agent.health <= 0:
            agents.remove(agent)
        elif agent.health > 160:
            agent.health /= 2
            add_agent(agent)

    food_to_spawn += configuration["Food_PerTick"]
    while food_to_spawn >= 1:
        food_to_spawn -= 1
        add_food()


def tick_agent(agent):
    global agents

    if tick_count-agent.birth == mark_agents_at_tick:
        agent.marked = True

    sensors = [configuration["Sensor_Food_Range"],
               configuration["Sensor_Food_Range"],
               configuration["Sensor_Food_Range"]]

    # Food
    for position in food_positions:
        # distance = agent.get_distance(position)
        distance = agent.get_fast_distance(position)
        if distance < 0.5 + configuration["Food_Diameter"] / 2:
            food_positions.remove(position)
            agent.eat()
        elif distance < configuration["Sensor_Food_Range"]:

            sensors = calculate_sensors(agent, position, distance, sensors)

    agent.sensors = sensors  # for agent.get_information_string

    # Neural Network
    agent.react(sensors)
    output = agent.output

    for i in range(0, len(output)):
        output[i] = confine_number(2*output[i]-1, -1, 1)

    # Movement
    agent.direction_change = output[0] * configuration["Agent_MaxTurningSpeed"]

    angle = agent.direction * 2 * math.pi

    agent.position_change_x = math.sin(angle) * output[1] * configuration["Agent_MaxMovementSpeed"]
    agent.position_change_y = math.cos(angle) * output[1] * configuration["Agent_MaxMovementSpeed"]

    # NaturalDecay
    agent.health -= configuration["Agent_NaturalDecay"]


def test_position(event):
    agents[0].highlighted = True
    food_position = [event.x, gui.area_in_px - event.y]
    for i in [0, 1]:
        food_position[i] = food_position[i] / gui.one_unit_in_px

    distance = agents[0].get_distance(food_position)

    print(calculate_sensors(agents[0], food_position, distance, [0, 0, 0]))


def calculate_sensors(agent, food_position, distance, sensors):

    direction = calculate_direction_difference(agent.position, food_position, agent.direction)

    size_middle = configuration["Sensor_Food_Middle_Angel"] / 360
    size_side = configuration["Sensor_Food_Side_Angel"] / 360
    if (1 - size_middle / 2 - size_side) < direction < (1 - size_middle / 2):
        if sensors[0] > distance:
            sensors[0] = distance

    elif direction < size_middle / 2 or direction > (1 - size_middle / 2):
        if sensors[1] > distance:
            sensors[1] = distance

    elif size_middle / 2 < direction < size_middle / 2 + size_side:
        if sensors[2] > distance:
            sensors[2] = distance

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
    global thread_tick_tasks

    print("########Start########")

    gui = Gui(configuration)

    gui.tkinter_root.protocol('WM_DELETE_WINDOW', quit_window)

    gui.tkinter_root.button_save.bind("<Button-1>", save)
    gui.tkinter_root.button_load.bind("<Button-1>", load)
    gui.tkinter_root.button_jump.bind("<Button-1>", jump)
    gui.tkinter_root.bind("y", jump)
    gui.tkinter_root.speed_slider.bind("<B1-Motion>", set_speed)
    gui.tkinter_root.speed_slider.bind("<Button-1>", set_speed)
    gui.tkinter_root.speed_slider.bind("<ButtonRelease-1>", set_speed)
    gui.tkinter_root.speed_slider.set(speed)

    # gui.tkinter_root.canvas.bind("<Button-1>", click_on_canvas)
    gui.tkinter_root.canvas.bind("<Button-1>", lambda event: gui.click_on_canvas(event, agents))
    gui.tkinter_root.bind("<space>", toggle_pause)
    gui.tkinter_root.tree_view.bind("<<TreeviewSelect>>", lambda event: gui.select_table(agents))

    # gui.tkinter_root.canvas.bind("<Button-1>", test_position)

    agents = []
    fill_to_min_population()
    gui.draw_frame(agents, food_positions, tick_count)

    thread_tick_tasks = []

    for i in range(0, number_of_threads):
        thread_tick_tasks.append(None)

        name = "thread "+str(i+1)+"/"+str(number_of_threads)
        thread = TickThread(i, name)
        thread.start()

    gui.tkinter_root.after(500, loop)
    gui.tkinter_root.mainloop()


def fill_to_min_population():
    while len(agents) < configuration["Agent_MinPopulation"]:
        add_agent()


def add_food():
    global food_positions
    position = [random.uniform(0, configuration["Area"]), random.uniform(0, configuration["Area"])]
    food_positions.append(position)


def add_agent(parent=None):
    global agents
    global tick_count

    position = [random.uniform(0, configuration["Area"]), random.uniform(0, configuration["Area"])]
    direction = random.uniform(0, 1)
    agent = Agent(position, direction, tick_count, configuration, parent)

    agents.append(agent)


# noinspection PyUnusedLocal
def toggle_pause(event):
    global speed
    global speed_before_pause

    if speed != 0:
        speed_before_pause = speed
        speed = 0
        gui.draw_frame(agents, food_positions, tick_count)
        gui.update_table(agents, tick_count)
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


# noinspection PyUnusedLocal
def jump(event):
    tick()


def quit_window():
    global exit_tasks

    exit_tasks = True
    gui.tkinter_root.destroy()


start()
