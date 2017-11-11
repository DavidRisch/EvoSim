import random
from math import exp

class NeuralNet:
    nLayers = 0
    nLayerNodes = [ ]

    layers = [ ]
    weights = [ ]
    biases = [ ]


    def __init__(self, nInNodes, nOutNodes, nHiddenLayerNodes):
        # input layer (first element in 'layers')
        self.layers = [ [ 0.0 for i in range(nInNodes) ] ]
        self.nLayerNodes.append(nInNodes)
        # hidden layers
        self.layers.extend([ [ 0.0 for j in range(i) ] for i in nHiddenLayerNodes ])
        self.nLayerNodes.extend(nHiddenLayerNodes)
        # output layer (last element in 'layers')
        self.layers.append([ 0.0 for i in range(nOutNodes) ])
        self.nLayerNodes.append(nOutNodes)

        self.nLayers = len(self.nLayerNodes)

        # weights [layer - 1] [node in hidden layer] [node in prev layer]
        self.weights = [ [ [ 0.5
            for i in range(self.nLayerNodes[k-1]) ]
            for j in range(self.nLayerNodes[k]) ]
            for k in range(1, self.nLayers) ]
        # biases [layer - 1] [node]
        self.biases = [ [ 0.0 for i in range(self.nLayerNodes[j]) ] for j in range(1, self.nLayers) ]

    
    def feed(self, inputData):
        self.layers[0] = inputData
        for i in range(1, self.nLayers):
            for j in range(self.nLayerNodes[i]):
                node = self.biases[i-1][j]
                for k in range(self.nLayerNodes[i-1]):
                    node += self.layers[i-1][k] * self.weights[i-1][j][k]
                self.layers[i][j] = 1 / (1 + exp( -node ))

        return self.layers[-1]


    def mutate_absolute(self, delta, seed=None):
        if seed != None:
            random.seed(seed)

        for i in range(self.nLayers - 1):
            for j in range(self.nLayerNodes[i+1]):
                for k in range(self.nLayerNodes[i]):
                    self.weights[i][j][k] += delta * random.randint(-500, 500) / 500.0


    def mutate(self, sigma, seed=None):
        if seed != None:
            random.seed(seed)

        for i in range(self.nLayers - 1):
            for j in range(self.nLayerNodes[i+1]):
                for k in range(self.nLayerNodes[i]):
                    self.weights[i][j][k] *= 1 + random.randint(-500, 500) / 500.0
