import math
from neuralnet import NeuralNet


class Agent:
    position = []
    direction = None  # 0 to 1 clockwise, 0 is facing up
    health = None
    birth = None
    configuration = {}
    neuralNet = None
    sensors = []
    output = []
    highlighted = False
    marked = False
    generation = 0

    def __init__(self, position, direction, tick_count, configuration, parent=None):
        # print("NewAgent")
        self.position = position
        self.direction = direction
        self.health = configuration["Agent_Health"]
        self.birth = tick_count
        self.configuration = configuration
        if parent is None:
            self.neuralNet = NeuralNet([3, 3, 2])
            self.neuralNet.randomize_weights(-10, 10)
        else:
            self.neuralNet = parent.neuralNet
            self.mutate()
            self.generation = parent.generation + 1

    def eat(self):
        self.health += self.configuration["Food_Value"]

    def get_distance(self, position):
        distance_x = self.position[0] - position[0]
        distance_y = self.position[1] - position[1]
        distance = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))
        return distance

    def get_information_string(self, tick_count):
        string = "Sensors: [" + ", ".join(str(e) for e in self.sensors) + "]\n"
        string += "Output: [" + ", ".join(str(e) for e in self.output) + "]\n"
        string += "Position: [" + str(round(self.position[0], 2)) + ", " + str(round(self.position[1], 2)) + "]\n"
        string += "Health: " + str(round(self.health, 2)) + "\n"
        string += "Age: " + str(tick_count - self.birth) + "\n"

        return string

    def react(self, sensors):
        self.output = self.neuralNet.feed(sensors)

    def mutate(self):
        self.neuralNet.mutate(0.1)
