import numpy
import matplotlib.pyplot
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

GATE_ARRAY_OFFSET = 5

def get_C():
    f = open("place.tiny", "r")
    
    # Read placement grid rows/columns
    grid_dims = f.readline().replace('\n','').split(' ')

    # Keep track of net IDs and which gates are connected to each net ID (1-?)
    # First index represents the net ID and stores a list of gates connected to this net ID.
    netlist = [[] for y in range(int(grid_dims[1])-1)]

    num_gates = 0

    # Populate netlist and C
    for line in f:
        if (line == "-1\n"):
            continue

        # Handle gate
        elif line.split(' ')[1] == 'g':
            line = line.replace('\n','').split(' ')
            num_connections = line[2]

            # num_gates = line[0]
            num_gates += 1

            # Populate netlist and connections
            for i in range(0, int(num_connections)):
                netlist[int(line[i+3])].append(int(line[0]))

    f.close()

    # print(num_gates)
    C = [[0 for x in range(int(num_gates))] for y in range(int(num_gates))]
    
    # Determine wire weights for multipoint wires -- assume W=1
    k = [0 for y in range(len(netlist))]
    weights = [0 for y in range(len(netlist))]
    for i in range(0, len(k)):
        k[i] = len(netlist[i])   # Find k

        # This is a multipoint wire
        if k[i] > 1:
            weights[i] = 1/(k[i]-1)
        else:
            weights[i] = k[i]

    # Fix C matrix with calculated weights
    f = open("place.tiny", "r")
    
    # Re-iterate over file, updating weights
    for line in f:
        if (line == "-1\n"):
            continue

        # Handle gate
        elif line.split(' ')[1] == 'g':
            line = line.replace('\n','').split(' ')

            gate_id = line[0]
            num_connections = line[2]

            # Populate netlist and connections
            for i in range(3, int(num_connections)+3):
                net_id = line[i]
                for gate in netlist[int(net_id)]:
                    if int(gate_id) != int(gate):
                        # print("so gate {} and gate {} are connected".format(int(gate_id), int(gate)))
                        C[int(gate_id)-GATE_ARRAY_OFFSET][int(gate)-GATE_ARRAY_OFFSET] += int(weights[int(net_id)])
                        C[int(gate)-GATE_ARRAY_OFFSET][int(gate_id)-GATE_ARRAY_OFFSET] += int(weights[int(net_id)])
    f.close()

    return C

def get_A(C):

    # Initialize A matrix from C dimensions
    A = [[0 for x in range(len(C))] for y in range(len(C[0]))] 

    for j in range(0, len(C[0])):
        for i in range(0, len(C)):

            # Non-diagonal case
            if i != j:
                A[i][j] = -1 * C[i][j]

            # Diagonal case
            elif i == j:
                for k in range(0, len(C[0])):
                    A[i][i] += C[i][k]
    return A

# Get b x or y
def get_b(C, char):
    f = open("place.tiny", "r")

    b = [0 for x in range(len(C))]
    
    for line in f:
        if (line == "-1\n"):
            continue

        # Get b x or y from pin connections
        if line.split(' ')[1] == 'p':
            line = line.replace('\n','').split(' ')
            # print(line)

            # (-1) * x position * weight
            if char == 'x':
                b[int(line[4])] = (-1) * int(line[2])
            elif char == 'y':
                b[int(line[4])] = (-1) * int(line[3])

    f.close()
    return b

def main():

    C = get_C()                 # Get C matrix
    # for line in C:
    #     print(line)

    # print()

    A = get_A(C)                # Get matrix A 
    # for line in A:
    #     print(line)

    # print()

    b_x = get_b(C, 'x')         # Get b_x
    # print(b_x)

    # print()

    b_y = get_b(C, 'y')         # Get b_y
    # print(b_y)

    # TODO: Solve quadratic placement using these matrices
    A = coo_matrix(A)

    print(A)
    x = spsolve(A.tocsr(), b_x)
    y = spsolve(A.tocsr(), b_y)

    # TODO: Visualize results of placement. Plot (x[i], y[i])
    # matplotlib.pyplot.scatter(x, y)
    # matplotlib.pyplot.show()

    print(x)
    print(y)

if __name__ == "__main__":
    main()

