import math
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

    def __init__(self, position, direction, tick_count, configuration, parent=None):
        self.position = position
        self.direction = direction
        self.health = configuration["Agent_Health"]
        self.birth = tick_count
        self.configuration = configuration
        if parent is None:
            self.neural_network = NeuralNetwork(configuration["Neural_Network_Nodes_In_Layers"])
            self.neural_network.randomize_weights(-10, 10)
        else:
            self.neural_network = parent.neural_network
            self.mutate()
            self.generation = parent.generation + 1

    def eat(self):
        self.health += self.configuration["Food_Value"]

    def get_distance(self, position):
        distance_x = self.position[0] - position[0]
        distance_y = self.position[1] - position[1]
        distance = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))
        return distance

    # fast algorithm, assuming the exact distance is only from importance, if
    # it is within the Sensor_Food_Range.
    # for correct measurement use get_distance()
    def get_fast_distance(self, position):
        dx = self.position[0] - position[0]
        dy = self.position[1] - position[1]
        food_range = self.configuration["Sensor_Food_Range"]
        if 2*abs(dx) <= food_range and 2*abs(dy) <= food_range:
            return math.sqrt(dx ** 2 + dy ** 2)
        else:
            return food_range + 1

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
        self.neural_network.mutate_absolute(self.configuration["Neural_Network_Mutate"])
