import random
from math import exp
from math import fsum


class NeuralNetwork:
    number_of_layers = 0     # old: nLayers
    nodes_in_layers = []     # old: nLayerNodes
    softmax = False

    layers = []
    weights = []
    biases = []

    def __init__(self, layer_nodes, softmax=True):
        self.layers = [[0.0 for i in range(j)] for j in layer_nodes]
        self.nodes_in_layers = layer_nodes
        self.softmax = softmax

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

                # ReLU activation function
                if node > 0:
                    self.layers[i][j] = node
                else:
                    self.layers[i][j] = 0
                ## switch calculation for sigmoid to
                ## avoid very large exp-function values
                #if node > 0:
                #    self.layers[i][j] = 1 / (1 + exp(-node))
                #else:
                #    self.layers[i][j] = exp(node) / (1 + exp(node))

        if self.softmax:
            sigmoid = lambda x: 1/(1+exp(-x)) if x>0 else exp(x)/(1+exp(x))

            out = [ sigmoid(self.layers[-1][i]) for i in range(self.nodes_in_layers[-1]) ]
            return out
            #try:
            #    out = [self.layers[-1][i] / fsum([exp(self.layers[-1][j]) for j in range(self.nodes_in_layers[-1])]) for i in range(self.nodes_in_layers[-1])]
            #    return out
            #except OverflowError:
            #    print(self.layers[-1])
            #    return [0,0,0]
        else:
            return self.layers[-1]

    def mutate(self, sigma):
        for i in range(1, self.number_of_layers):
            for j in range(self.nodes_in_layers[i]):
                self.biases[i-1][j] = random.gauss(self.biases[i-1][j], sigma)
                for k in range(self.nodes_in_layers[i-1]):
                    self.weights[i-1][j][k] = random.gauss(self.weights[i-1][j][k], sigma)
