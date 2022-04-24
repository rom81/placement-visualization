##################################################################################################
# This is an analytical placement and visualizer tool which uses quadratic placement to place
# movable gates on a grid with immovable pins. 
##################################################################################################

import numpy
import matplotlib.pyplot
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

GATE_ARR_OFFSET = 5
PLACEMENT_FILENAME = "place.tiny"

##################################################################################################
# Find the total number of gates in this file
##################################################################################################
def get_num_gates():
    
    num_gates = 0

    # Find number of gates
    f = open(PLACEMENT_FILENAME, "r")
    for line in f:
        line = line.replace('\n','').split(' ')

        # Found end-of-file sentinel
        if (int(line[0]) == -1):
            continue

        # Handle gate
        elif line[1] == 'g':
            num_gates += 1

    f.close()
    return num_gates
##################################################################################################

##################################################################################################
# Read netlist from file
##################################################################################################
def get_gate_only_netlist():

    f = open(PLACEMENT_FILENAME, "r")
    
    # Read placement grid rows/columns
    grid_dims = f.readline().replace('\n','').split(' ')

    # Keep track of net IDs and which gates are connected to each net ID 
    # Index represents the net ID and stores a list of gates connected to this net ID.
    netlist = [[] for y in range(int(grid_dims[0]))]

    for line in f:
        line = line.replace('\n','').split(' ')

        # Found end-of-file sentinel
        if (int(line[0]) == -1):
            continue

        # Handle gate
        elif line[1] == 'g':
            num_connections = int(line[2])
            gate_id = int(line[0])

            # Populate netlist and connections
            for i in range(0, num_connections):
                net_id = int(line[i+3])
                netlist[net_id].append(gate_id)

    f.close()

    return netlist
##################################################################################################
# Return an object representing which gates are connected to which pins
##################################################################################################
def get_pinlist(netlist):
    f = open(PLACEMENT_FILENAME, "r")

    pinlist = {}  # Specifies which pin(s) are connected to which gate(s)

    for line in f:
        line = line.replace('\n','').split(' ')

        # Found end-of-file sentinel
        if (int(line[0]) == -1):
            continue

        # Handle nets connected to pins
        elif line[1] == 'p':
            pin_id = int(line[0])
            net_id = int(line[4])

            # check which gates are connected to net_id
            pinlist[pin_id] = []
            for gate_id in netlist[net_id]:
                pinlist[pin_id].append(gate_id)

    f.close()

    return pinlist
##################################################################################################
# Calculate wire weights for both 2-point and multipoint nets
##################################################################################################
def calculate_weights(netlist):

    W = 1 # Assume W = 1
    k = [0 for y in range(len(netlist))]
    weights = [0 for y in range(len(netlist))]

    for i in range(0, len(k)):

        k[i] = len(netlist[i])   # Find k

        # This is a multipoint wire
        if k[i] > 1:
            weights[i] = W/(k[i]-1)

        # This is a 2-point wire
        else:
            weights[i] = k[i]

    return weights
##################################################################################################

##################################################################################################
# Compute C matrix
##################################################################################################
def get_C(netlist, num_gates):

    # Define size of C matrix based on number of gates
    C = [[0 for x in range(int(num_gates))] for y in range(int(num_gates))]
    weights = calculate_weights(netlist)  # Determine wire weights for netlist

    f = open(PLACEMENT_FILENAME, "r")
    for line in f:
        line = line.replace('\n','').split(' ')

        # Found end-of-file sentinel
        if (int(line[0]) == -1):
            continue

        # Handle gate
        elif line[1] == 'g':
            gate_id = int(line[0])
            num_connections = int(line[2])

            # Populate netlist and connections
            for i in range(3, num_connections + 3):
                net_id = int(line[i])
                for gate in netlist[net_id]:
                    gate = int(gate)
                    if gate_id != gate:
                        C[gate_id-GATE_ARR_OFFSET][gate-GATE_ARR_OFFSET] += int(weights[net_id])
                        C[gate-GATE_ARR_OFFSET][gate_id-GATE_ARR_OFFSET] += int(weights[net_id])

    f.close()

    return C
##################################################################################################
# Return true if gate_d is connected to a pin in pinlist. 
# TODO: This function currently assumes that one pin is connected to at most one gate and that the
# net has a weight of 1. This is true for place.tiny but might not be true for other file.
##################################################################################################
def gate_is_connected_to_a_pin(gate_id, pinlist):

    for list_of_pins in pinlist.values():
        if gate_id in list_of_pins:
            return True

    return False
##################################################################################################

##################################################################################################
# Compute A matrix
################################################################################################## 
def get_A(C, pinlist):

    # Initialize A matrix from C dimensions
    A = [[0 for x in range(len(C))] for y in range(len(C[0]))] 

    for j in range(0, len(C[0])):
        for i in range(0, len(C)):

            # Non-diagonal case
            if i != j:
                A[i][j] = -1 * C[i][j]

            # Diagonal case
            # i and j represent an index in A or C. this index + GATE_ARR_OFFSET is the gate_id. 
            elif i == j:
                for k in range(0, len(C[0])):
                    A[i][i] += C[i][k]

                # If gate i is connected to a pin, increment A[i][i] by weight of wire 
                if gate_is_connected_to_a_pin(i + GATE_ARR_OFFSET, pinlist):
                    A[i][i] += 1        # TODO: Change this to the weight
                
    return A
##################################################################################################

##################################################################################################
# Get b x or y
##################################################################################################
def get_b(C, char, netlist):

    b = [0 for x in range(len(C))]
    weights = calculate_weights(netlist)
    f = open(PLACEMENT_FILENAME, "r")

    for line in f:
        line = line.replace('\n','').split(' ')

        # Found end-of-file sentinel
        if (int(line[0]) == -1):
            continue
    
        # Get b_x or b_y from pin connections
        elif line[1] == 'p':
            net_id = int(line[4])
            x_coord = int(line[2])
            y_coord = int(line[3])
            for gate in netlist[net_id]:

                # b[this gate] = position * weight
                if char == 'x':
                    b[gate-GATE_ARR_OFFSET] = x_coord * weights[net_id]

                elif char == 'y':
                    b[gate-GATE_ARR_OFFSET] = y_coord * weights[net_id]

    f.close()

    return b
##################################################################################################

##################################################################################################
def main():
    netlist = get_gate_only_netlist()     # Get netlist
    num_gates = get_num_gates()           # Find number of gates
    C = get_C(netlist, num_gates)         # Get C matrix
    pinlist = get_pinlist(netlist)        # Find pin-gate connections
    A = get_A(C, pinlist)                 # Get A matrix
    b_x = get_b(C, 'x', netlist)          # Get b_x
    b_y = get_b(C, 'y', netlist)          # Get b_y

    # Solve quadratic placement using these matrices
    A = coo_matrix(A)
    
    x = spsolve(A.tocsr(), b_x)          # Ax = -b_x
    y = spsolve(A.tocsr(), b_y)          # Ay = -b_y

    # Visualize results of placement. Plot (x[i], y[i])
    matplotlib.pyplot.scatter(x, y)
    matplotlib.pyplot.xlim([0, 61])
    matplotlib.pyplot.ylim([0, 61])
    matplotlib.pyplot.show()

if __name__ == "__main__":
    main()
