import math


class Agent:
    position = []
    direction = None
    health = None
    birth = None
    configuration = {}

    def __init__(self, position, direction, tick_count, configuration):
        # print("NewAgent")
        self.position = position
        self.direction = direction
        self.health = configuration["Agent_Health"]
        self.birth = tick_count
        self.configuration = configuration

    def eat(self):
        self.health += self.configuration["Food_Value"]

    def get_distance(self, position):
        distance_x = self.position[0] - position[0]
        distance_y = self.position[1] - position[1]
        distance = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))
        return distance

    def get_information_string(self, tick_count, sensors, output):
        string = "Sensors: [" + ", ".join(str(e) for e in sensors) + "]\n"
        string = "Output: [" + ", ".join(str(e) for e in output) + "]\n"
        string += "Position: [" + str(round(self.position[0], 2)) + ", " + str(round(self.position[1], 2)) + "]\n"
        string += "Health: " + str(round(self.health, 2)) + "\n"
        string += "Age: " + str(tick_count - self.birth) + "\n"


