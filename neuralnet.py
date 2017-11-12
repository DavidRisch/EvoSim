import random
from math import exp


class NeuralNet:
    nLayers = 0
    nLayerNodes = []

    layers = []
    weights = []
    biases = []

    def __init__(self, in_nodes, hidden_layer_nodes, out_nodes):
        # input layer (first element in 'layers')
        self.layers = [[0.0 for i in range(in_nodes)]]
        self.nLayerNodes.append(in_nodes)
        # hidden layers
        self.layers.extend([[0.0 for j in range(i)]
                            for i in hidden_layer_nodes])
        self.nLayerNodes.extend(hidden_layer_nodes)
        # output layer (last element in 'layers')
        self.layers.append([0.0 for i in range(out_nodes)])
        self.nLayerNodes.append(out_nodes)

        self.nLayers = len(self.nLayerNodes)

        # weights [layer - 1] [node in hidden layer] [node in prev layer]
        self.weights = [[[0.0
                        for i in range(self.nLayerNodes[k-1])]
                        for j in range(self.nLayerNodes[k])]
                        for k in range(1, self.nLayers)]
        # biases [layer - 1] [node]
        self.biases = [[0.0 for i in range(self.nLayerNodes[j])]
                       for j in range(1, self.nLayers)]

    def feed(self, input_data):
        self.layers[0] = input_data
        for i in range(1, self.nLayers):
            for j in range(self.nLayerNodes[i]):
                node = self.biases[i-1][j]
                for k in range(self.nLayerNodes[i-1]):
                    node += self.layers[i-1][k] * self.weights[i-1][j][k]

                # switch calculation for sigmoid to
                # avoid very large exp-function values
                if abs(node) > 1e-2:
                    self.layers[i][j] = 1 / (1 + exp(-node))
                else:
                    self.layers[i][j] = exp(node) / (1 + exp(node))

        return self.layers[-1]

    def randomize_weights(self, wmin, wmax, seed=None):
        if seed is None:
            random.seed(seed)

        for i in range(self.nLayers - 1):
            for j in range(self.nLayerNodes[i]):
                for k in range(self.nLayerNodes[i-1]):
                        self.weights[i][j][k] = wmin + (wmax-wmin) \
                                                * random.random()

    def mutate_absolute(self, delta, seed=None):
        if seed is None:
            random.seed(seed)

        for i in range(self.nLayers - 1):
            for j in range(self.nLayerNodes[i+1]):
                for k in range(self.nLayerNodes[i]):
                    self.weights[i][j][k] += delta * (2 * random.random() - 1)

    def mutate(self, sigma, seed=None):
        if seed is None:
            random.seed(seed)

        for i in range(self.nLayers - 1):
            for j in range(self.nLayerNodes[i+1]):
                for k in range(self.nLayerNodes[i]):
                    self.weights[i][j][k] *= 1 + sigma \
                                * (2 * random.random() - 1)
