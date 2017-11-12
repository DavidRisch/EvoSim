import datetime
import json


def save(data):
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file = open("saves/"+(filename+".txt"), "w")

    string = json.JSONEncoder().encode(data)

    file.write(string)
    file.close()

    # def load(self, filename):
