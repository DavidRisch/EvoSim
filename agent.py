import math
from copy import deepcopy
from neuralnet import NeuralNetwork


class Agent:
    position = []
    direction = None  # 0 to 1 clockwise, 0 is facing up
    position_change_x = 0  # TODO: store as array (causes bug)
    position_change_y = 0
    direction_change = None
    health = None
    birth = None
    configuration = {}
    neural_network = None
    sensors = []
    output = []
    highlighted = False
    marked = False
    generation = 0
    last_attacked_by = None

    def __init__(self, position, direction, tick_count, configuration, parent=None):
        self.position = position
        self.direction = direction
        self.health = configuration["Agent_Health"]
        self.birth = tick_count
        self.configuration = configuration
        if parent is None:
            self.neural_network = NeuralNetwork(configuration["Neural_Network_Nodes_In_Layers"])
            self.neural_network.mutate(10)
        else:
            self.neural_network = deepcopy(parent.neural_network)
            self.generation = parent.generation + 1
            self.mutate()

    def eat(self):
        self.health += self.configuration["Food_Value"]

    def perform_attack(self, agents):
        self.health -= self.configuration["Agent_Attack_Cost"]

        for agent in agents:
            if agent != self:
                distance = self.get_distance(agent.position, self.configuration["Agent_Attack_Range"])
                if distance < self.configuration["Agent_Attack_Range"]:
                    agent.get_attacked(self)

    def get_attacked(self, other_agent):
        self.health -= self.configuration["Agent_Attack_Damage"]

        self.last_attacked_by = other_agent

    def get_distance(self, position, max_range):
        distance_x = self.position[0] - position[0]
        distance_y = self.position[1] - position[1]

        if abs(distance_x) <= max_range and abs(distance_y) <= max_range:
            distance = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))
            return distance
        else:
            return 999999

    def get_information_string(self, tick_count):
        string = "Sensors: [" + ", ".join(str(e) for e in self.sensors) + "]\n"
        string += "Output: [" + ", ".join(str(e) for e in self.output) + "]\n"
        string += "Position: [" + str(round(self.position[0], 2)) + ", " + str(round(self.position[1], 2)) + "]\n"
        string += "Health: " + str(round(self.health, 2)) + "\n"
        string += "Age: " + str(tick_count - self.birth) + "\n"
        string += "Generation: " + str(self.generation) + "\n"

        return string

    def react(self, sensors):
        self.output = self.neural_network.feed(sensors)

    def mutate(self):
        self.neural_network.mutate(self.configuration["Neural_Network_Mutate"])
