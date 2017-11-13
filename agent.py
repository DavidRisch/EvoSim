import math
from neuralnet import NeuralNet


class Agent:
    position = []
    angle = None  # 0 means to the right
    health = None
    birth = None
    configuration = {}
    neuralNet = None
    output = [0, 0]
    highlighted = False

    def __init__(self, position, angle, tick_count, configuration, neural_net=None):
        # print("NewAgent")
        self.position = position
        self.health = configuration["Agent_Health"]
        self.birth = tick_count
        self.configuration = configuration
        self.angle = angle

        if neural_net is None:
            self.neuralNet = NeuralNet([3, 2])
            self.neuralNet.randomize_weights(-0.5, 0.5)
        else:
            self.neuralNet = neural_net
            self.neuralNet.mutate_absolute(0.1)

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
        string += "Angle: " + str(round(self.angle, 2)) + "\n"
        string += "Health: " + str(round(self.health, 2)) + "\n"
        string += "Age: " + str(tick_count - self.birth) + "\n"

        return string

    def react(self, sensors):
        self.sensors = sensors
        self.output = self.neuralNet.feed(sensors)
        self.angle += 2 * self.output[0] * math.pi * self.configuration["Agent_MaxTurningSpeed"] / 360

        # TODO: more efficient implementation
        while self.angle < 0:
            self.angle += 2 * math.pi
        while self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi

    def mutate(self):
        self.neuralNet.mutate_absolute(0.5)
