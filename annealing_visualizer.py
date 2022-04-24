##################################################################################################
# This is a tool for visualizing placement from a simulated annealing placer
##################################################################################################

import numpy
import matplotlib.pyplot
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve


##################################################################################################
def main():
    x = []
    y = []

    # Read in placement
    f = open("place-tiny.out", "r")

    for line in f:
        line = line.replace('\n','').split(' ')

        x.append(int(line[2]))
        y.append(int(line[3]))

    print(x)
    print(y)
        
    # TODO: Visualize placement. Plot (x[i], y[i])
    matplotlib.pyplot.scatter(x, y)
    matplotlib.pyplot.xlim([0, 61])
    matplotlib.pyplot.ylim([0, 61])
    matplotlib.pyplot.show()
    return

if __name__ == "__main__":
    main()
