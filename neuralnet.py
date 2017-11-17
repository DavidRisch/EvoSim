import random
from math import exp


class NeuralNetwork:
    number_of_layers = 0     # old: nLayers
    nodes_in_layers = []     # old: nLayerNodes

    layers = []
    weights = []
    biases = []

    def __init__(self, layer_nodes):
        self.layers = [[0.0 for i in range(j)] for j in layer_nodes]
        self.nodes_in_layers = layer_nodes

        self.number_of_layers = len(self.nodes_in_layers)

        # weights [layer - 1] [node in hidden layer] [node in prev layer]
        self.weights = [[[0.0
                          for i in range(self.nodes_in_layers[k - 1])]
                         for j in range(self.nodes_in_layers[k])]
                        for k in range(1, self.number_of_layers)]
        # biases [layer - 1] [node]
        self.biases = [[0.0 for i in range(self.nodes_in_layers[j])]
                       for j in range(1, self.number_of_layers)]

    def feed(self, input_data):
        self.layers[0] = input_data
        for i in range(1, self.number_of_layers):
            for j in range(self.nodes_in_layers[i]):
                node = self.biases[i-1][j]
                for k in range(self.nodes_in_layers[i-1]):
                    node += self.layers[i-1][k] * self.weights[i-1][j][k]

                # switch calculation for sigmoid to
                # avoid very large exp-function values
                if node > 0:
                    self.layers[i][j] = 1 / (1 + exp(-node))
                else:
                    self.layers[i][j] = exp(node) / (1 + exp(node))

        return self.layers[-1]

    def mutate(self, sigma):
        for i in range(1, self.number_of_layers):
            for j in range(self.nodes_in_layers[i]):
                self.biases[i-1][j] = random.gauss(self.biases[i-1][j], sigma)
                for k in range(self.nodes_in_layers[i-1]):
                    self.weights[i-1][j][k] = random.gauss(self.weights[i-1][j][k], sigma)
