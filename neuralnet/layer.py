import numpy as np

class Layer:
    nodes = []

    def __init__(self, inodes):
        nodes = np.array([ 0.0 for i in range(inodes) ])
