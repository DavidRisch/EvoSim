import methods
from agent import Agent

import time
import math
import random
import threading


class Manager:
    configuration = {}
    agents = []
    food_positions = []
    tick_count = 0
    food_to_spawn = 0
    # keeps track of food, that needs to be spawned (because configuration["Food_PerTick"] is not an int)

    fps = 20
    fps_table = 5
    last_frame_ms = 0
    last_table_frame_ms = 0
    speed = 20  # ticks/second
    speed_before_pause = 0
    wait_ever_x_ticks = 25  # prevent program from freezing
    number_of_threads = 8

    mark_agents_at_tick = 2000

    thread_tick_tasks = []
    exit_tasks = False

    gui = None

    def __init__(self, configuration, gui):
        self.configuration = configuration
        self.gui = gui
        self.gui.bind_buttons(self)

        gui.tkinter_root.speed_slider.set(self.speed)

        self.fill_to_min_population()
        gui.draw_frame()

        self.thread_tick_tasks = []

        for i in range(0, self.number_of_threads):
            self.thread_tick_tasks.append(None)

            name = "thread " + str(i + 1) + "/" + str(self.number_of_threads)
            thread = TickThread(self, i, name)
            thread.start()

        gui.tkinter_root.after(500, self.loop)

    def loop(self):
        start_ms = time.time() * 1000.0

        if self.speed != 0:
            self.tick()

        current_ms = time.time() * 1000.0

        if current_ms >= self.last_frame_ms + round((1 / self.fps) * 1000):
            self.last_frame_ms = current_ms
            self.gui.draw_frame()

        if current_ms >= self.last_table_frame_ms + round((1 / self.fps_table) * 1000):
            self.last_table_frame_ms = current_ms
            self.gui.update_table()

        if self.speed != 0:
            time_to_next_tick = round((1 / self.speed) * 1000 - (current_ms - start_ms))
        else:
            time_to_next_tick = round((1 / 20) * 1000)  # 25fps

        if time_to_next_tick <= 1 and self.tick_count % self.wait_ever_x_ticks == 0:
            time_to_next_tick = 1

        self.gui.tkinter_root.after(time_to_next_tick, self.loop)

    def tick(self):
        self.tick_count += 1

        self.fill_to_min_population()

        for i in range(0, self.number_of_threads):
            self.thread_tick_tasks[i] = self.agents[i::self.number_of_threads]

        tasks_complete = False
        while not tasks_complete:
            time.sleep(0.0001)  # 0.1ms
            tasks_complete = True
            for tick_tasks in self.thread_tick_tasks:
                if tick_tasks is not None:
                    tasks_complete = False

        for agent in self.agents:
            agent.direction += agent.direction_change
            agent.direction = methods.wrap_direction(agent.direction)
            agent.position[0] += agent.position_change_x
            agent.position[1] += agent.position_change_y
            agent.position = methods.wrap_position(agent.position, self.configuration)

        for agent in self.agents:
            if agent.health <= 0:
                if agent.last_attacked_by is not None:
                    agent.last_attacked_by.health += self.configuration["Agent_Attack_Gain"]
                self.agents.remove(agent)
            elif agent.health >= self.configuration["Agent_Reproduce_At"]:
                agent.health -= self.configuration["Agent_Reproduce_Cost"]
                self.add_agent(agent)

            agent.last_attacked_by = None

        self.food_to_spawn += self.configuration["Food_PerTick"]
        while self.food_to_spawn >= 1:
            self.food_to_spawn -= 1
            self.add_food()

    def tick_agent(self, agent):
        if self.tick_count - agent.birth == self.mark_agents_at_tick:
            agent.marked = True

        sensors = [
            self.configuration["Sensor_Food_Range"],
            self.configuration["Sensor_Food_Range"],
            self.configuration["Sensor_Food_Range"],
            self.configuration["Sensor_Food_Range"],
            self.configuration["Sensor_Agent_Range"],
            self.configuration["Sensor_Agent_Range"],
            self.configuration["Sensor_Agent_Range"],
            self.configuration["Sensor_Agent_Range"],
            agent.health / self.configuration["Agent_Health"],
        ]

        # Food
        for food_position in self.food_positions:
            distance = agent.get_distance(food_position, self.configuration["Sensor_Food_Range"])
            if distance < 0.5 + self.configuration["Food_Diameter"] / 2:
                self.food_positions.remove(food_position)
                agent.eat()
            elif distance < self.configuration["Sensor_Food_Range"]:
                sensors = methods.calculate_sensors(agent, food_position, None, distance,
                                                    sensors, self.configuration)

        for other_agent in self.agents:
            if other_agent != agent:
                distance = agent.get_distance(other_agent.position, self.configuration["Sensor_Agent_Range"])
                if distance < self.configuration["Sensor_Agent_Range"]:
                    sensors = methods.calculate_sensors(agent, None, other_agent.position, distance,
                                                        sensors, self.configuration)

        agent.sensors = sensors  # for agent.get_information_string

        # Neural Network

        # Sensors: [Food_Left, Food_Middle, Food_Right, Food_Rest
        #           Agent_Left, Agent_Middle, Agent_Right, Agent_Rest
        #           health,]

        # Output:  [Rotation, Movement, Attack]

        agent.react(sensors)
        output = agent.output

        for i in range(0, len(output)):
            output[i] = methods.confine_number(2 * output[i] - 1, -1, 1)

        # Movement
        agent.direction_change = output[0] * self.configuration["Agent_Turning_MaxSpeed"]

        angle = agent.direction * 2 * math.pi

        agent.position_change_x = math.sin(angle) * output[1] * self.configuration["Agent_Movement_MaxSpeed"]
        agent.position_change_y = math.cos(angle) * output[1] * self.configuration["Agent_Movement_MaxSpeed"]
        agent.health -= math.fabs(output[1]) * self.configuration["Agent_Movement_Cost"]

        # Attack
        if output[2] > 0:
            agent.perform_attack(self.agents)

        # NaturalDecay
        agent.health -= self.configuration["Agent_NaturalDecay"]

    def fill_to_min_population(self):
        while len(self.agents) < self.configuration["Agent_MinPopulation"]:
            self.add_agent()

    def add_food(self):
        position = [random.uniform(0, self.configuration["Area"]), random.uniform(0, self.configuration["Area"])]
        self.food_positions.append(position)

    def add_agent(self, parent=None):
        position = [random.uniform(0, self.configuration["Area"]), random.uniform(0, self.configuration["Area"])]
        direction = random.uniform(0, 1)
        agent = Agent(position, direction, self.tick_count, self.configuration, parent)

        self.agents.append(agent)


class TickThread (threading.Thread):
    def __init__(self, manager, thread_id, name):
        threading.Thread.__init__(self)
        self.manager = manager
        self.thread_id = thread_id
        self.name = name

    def run(self):
        print("Starting " + self.name)
        while not self.manager.exit_tasks:
            if self.manager.thread_tick_tasks[self.thread_id] is not None:
                for agent in list(self.manager.thread_tick_tasks[self.thread_id]):
                    if agent is not None:
                        self.manager.tick_agent(agent)

                        self.manager.thread_tick_tasks[self.thread_id] = None

            time.sleep(0.0001)  # 0.1ms
        print("Exiting " + self.name)
