import methods
from agent import Agent
from threads import TickThread

import time
import math
import random
from copy import copy


class FrameInformation:
    has_been_used = True
    is_being_used = False
    agents = []
    food_positions = []
    tick_count = 0


class Manager:
    configuration = {}
    agents = []
    food_positions = []
    tick_count = 0
    food_to_spawn = 0
    # keeps track of food, that needs to be spawned (because configuration["Food_PerTick"] is not an int)

    fps = 20
    last_frame_ms = 0
    speed = 20  # ticks/second
    speed_before_pause = 0
    # wait_ever_x_ticks = 25  # prevent program from freezing
    number_of_threads = 8

    mark_agents_at_tick = 2000

    thread_tick_tasks = []
    thread_tick_tasks_stage = [0 for i in range(0, number_of_threads)]
    exit_tasks = False
    frame_information = FrameInformation()

    def __init__(self, configuration):
        self.configuration = configuration

        self.fill_to_min_population()
        self.set_frame_information()

        self.thread_tick_tasks = []

        for i in range(0, self.number_of_threads):
            self.thread_tick_tasks.append(None)

            name = "thread " + str(i + 1) + "/" + str(self.number_of_threads)
            thread = TickThread(self, i, name)
            thread.start()

    def loop(self):
        while True:
            start_ms = time.time() * 1000.0

            if self.speed != 0:
                self.tick()

            current_ms = time.time() * 1000.0

            if current_ms >= self.last_frame_ms + round((1 / self.fps) * 1000):
                if not self.frame_information.is_being_used:
                    self.last_frame_ms = current_ms
                    self.set_frame_information()

            # print("tick: "+str(current_ms - start_ms))

            if self.speed != 0:
                time_to_next_loop = (1 / self.speed) * 1000 - (current_ms - start_ms)
            else:
                time_to_next_loop = (1 / 20) * 1000  # 20fps

            if time_to_next_loop < 0:
                time_to_next_loop = 0

            time.sleep(time_to_next_loop / 1000)

    def tick(self):
        self.tick_count += 1

        self.fill_to_min_population()

        for i in range(0, self.number_of_threads):
            self.thread_tick_tasks[i] = self.agents[i::self.number_of_threads]

        self.thread_tick_tasks_stage = [1 for i in range(0, self.number_of_threads)]
        self.wait_for_tick_thread_progress(2)
        self.thread_tick_tasks_stage = [3 for i in range(0, self.number_of_threads)]
        self.wait_for_tick_thread_progress(4)
        self.thread_tick_tasks_stage = [0 for i in range(0, self.number_of_threads)]

        self.food_to_spawn += self.configuration["Food_PerTick"]
        while self.food_to_spawn >= 1:
            self.food_to_spawn -= 1
            self.add_food()

    def tick_agent_part_a(self, agent):
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

    def tick_agent_part_b(self, agent):
        agent.direction += agent.direction_change
        agent.direction = methods.wrap_direction(agent.direction)
        agent.position[0] += agent.position_change_x
        agent.position[1] += agent.position_change_y
        agent.position = methods.wrap_position(agent.position, self.configuration)

        if agent.health <= 0:
            if agent.last_attacked_by is not None:
                agent.last_attacked_by.health += self.configuration["Agent_Attack_Gain"]
            self.agents.remove(agent)
        elif agent.health >= self.configuration["Agent_Reproduce_At"]:
            agent.health -= self.configuration["Agent_Reproduce_Cost"]
            self.add_agent(agent)

        agent.last_attacked_by = None

    def set_frame_information(self):
        self.frame_information.agents = copy(self.agents)
        self.frame_information.food_positions = copy(self.food_positions)
        self.frame_information.tick_count = self.tick_count
        self.frame_information.has_been_used = False

    def wait_for_tick_thread_progress(self, progress):
        tasks_complete = False
        while not tasks_complete:
            time.sleep(0.00005)  # 0.05ms
            tasks_complete = True
            for thread_tick_tasks_progress in self.thread_tick_tasks_stage:
                if thread_tick_tasks_progress != progress:
                    tasks_complete = False

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
