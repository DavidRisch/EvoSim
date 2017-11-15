from agent import Agent

import datetime
import json


def save(manager):
    print("Saving...")
    agents_data = []
    for agent in manager.agents:
        agent_data = {
            "position": agent.position,
            "direction": agent.direction,
            "health": agent.health,
            "birth": agent.birth,
            "generation": agent.generation,
            "neural_network": {
                "nodes_in_layers": agent.neural_network.nodes_in_layers,
                "layers": agent.neural_network.layers,
                "weights": agent.neural_network.weights,
                "biases": agent.neural_network.biases,
            },
        }
        agents_data.append(agent_data)

    data = {
        "configuration": manager.configuration,
        "agent_data": agents_data,
        "food_positions": manager.food_positions,
    }
    print(data)

    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file = open("saves/"+(filename+".EvoSim"), "w")

    string = json.JSONEncoder().encode(data)

    file.write(string)
    file.close()

    print("Saving complete")


def load(manager):
    print("Loading...")
    file_name = manager.gui.open_file_dialog()
    print(file_name)
    file = open(file_name, "r")
    data = json.JSONDecoder().decode(file.readline())

    manager.configuration = data["configuration"]

    agents_data = data["agent_data"]
    agents = []

    for agent_data in agents_data:
        position = agent_data["position"]
        direction = agent_data["direction"]
        birth = agent_data["birth"]

        agent = Agent(position, direction, birth, manager.configuration)
        agent.health = agent_data["health"]
        agent.generation = agent_data["generation"]

        neural_network_data = agent_data["neural_network"]
        agent.neural_network.nodes_in_layers = neural_network_data["nodes_in_layers"]
        agent.neural_network.weights = neural_network_data["weights"]
        agent.neural_network.biases = neural_network_data["biases"]

        agents.append(agent)

    manager.agents = agents

    manager.food_positions = data["food_positions"]

    print("Loading complete")
