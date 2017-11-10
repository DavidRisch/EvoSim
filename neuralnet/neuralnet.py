class NeuralNet:
    layers = []
    def __init__(self, ilayer, nodesPerList):
        layers = array([ Layer(nodesPerList[i]) for i in range(ilayer) ])
