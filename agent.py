import math

class Agent:
    position = []
    direction = None
    health = None
    birth = None
    configuration = {}
    tick_count = None

    def __init__(self, position, direction, tick_count, configuration):
        print("NewAgent")
        self.configuration = configuration
        self.position = position
        self.direction = direction
        self.health = configuration["Agent_Health"]
        self.birth = tick_count
        self.tick_count = tick_count


    def tick(self):
        self.tick_count += 1
        # Movement
        angle = self.direction * 2 * math.pi

        self.position[0] += math.sin(angle) * self.configuration["Agent_MaxSpeed"]
        self.position[1] += math.cos(angle) * self.configuration["Agent_MaxSpeed"]

        for i in [0, 1]:
            if self.position[i] < 0:
                self.position[i] = self.configuration["Area"] + self.position[i]
            if self.position[i] > self.configuration["Area"]:
                self.position[i] = self.configuration["Area"] - self.position[i]

        # NaturalDecay
        self.health -= self.configuration["Agent_NaturalDecay"]


    def eat(self):
        self.health += self.configuration["Food_Value"]


    def die(self):
        agents.remove(self)


    def get_distance(self, position):
        distance_x = self.position[0] - position[0]
        distance_y = self.position[1] - position[1]
        distance = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))
        return distance


    def get_information_string(self):
        string = "Position: [" + str(round(self.position[0], 2)) + ", " + str(round(self.position[1], 2)) + "]\n"
        string += "Health: " + str(round(self.health, 2)) + "\n"
        string += "Age: " + str(self.tick_count - self.birth) + "\n"

        return string
