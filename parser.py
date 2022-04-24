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
    f = open(PLACEMENT_FILENAME, "r")
    
    # Read placement grid rows/columns
    grid_dims = f.readline().replace('\n','').split(' ')

    num_gates = 0

    # First pass: find number of gates and generate netlist
    for line in f:
        if (line == "-1\n"):
            continue

        # Handle gate
        elif line.split(' ')[1] == 'g':
            line = line.replace('\n','').split(' ')
            num_gates += 1

    f.close()
    return num_gates
##################################################################################################

##################################################################################################
# Read netlist from file
##################################################################################################
def get_netlist():
    f = open(PLACEMENT_FILENAME, "r")
    
    # Read placement grid rows/columns
    grid_dims = f.readline().replace('\n','').split(' ')

    # Keep track of net IDs and which gates are connected to each net ID (1-?)
    # First index represents the net ID and stores a list of gates connected to this net ID.
    netlist = [[] for y in range(int(grid_dims[1])-1)]

    # First pass: find number of gates and generate netlist
    for line in f:
        if (line == "-1\n"):
            continue

        # Handle gate
        elif line.split(' ')[1] == 'g':
            line = line.replace('\n','').split(' ')
            num_connections = int(line[2])
            gate_id = int(line[0])

            # Populate netlist and connections
            for i in range(0, num_connections):
                net_id = int(line[i+3])
                netlist[net_id].append(gate_id)

    f.close()

    return netlist
##################################################################################################

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
    
    # Determine wire weights for multipoint wires -- assume W=1
    weights = calculate_weights(netlist)

    f = open(PLACEMENT_FILENAME, "r")
    
    for line in f:

        if (line == "-1\n"):
            continue

        # Handle gate
        elif line.split(' ')[1] == 'g':

            line = line.replace('\n','').split(' ')
            gate_id = int(line[0])
            num_connections = int(line[2])

            # Populate netlist and connections
            for i in range(3, num_connections + 3):

                net_id = int(line[i])

                for gate in netlist[net_id]:

                    gate = int(gate)

                    if gate_id != gate:
                        
                        # print("so gate {} and gate {} are connected" \
                        #   .format(gate_id, int(gate)))
                        C[gate_id-GATE_ARR_OFFSET][gate-GATE_ARR_OFFSET] += int(weights[net_id])
                        C[gate-GATE_ARR_OFFSET][gate_id-GATE_ARR_OFFSET] += int(weights[net_id])

    f.close()

    return C
##################################################################################################

##################################################################################################
# Compute A matrix
################################################################################################## 
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
##################################################################################################


##################################################################################################
# Get b x or y
##################################################################################################
def get_b(C, char, netlist):

    f = open(PLACEMENT_FILENAME, "r")

    b = [0 for x in range(len(C))]

    weights = calculate_weights(netlist)
    
    for line in f:

        if (line == "-1\n"):
            continue
    
        # Get b_x or b_y from pin connections
        elif line.split(' ')[1] == 'p':
            
            line = line.replace('\n','').split(' ')

            net_id = int(line[4])
            x_coord = int(line[2])
            y_coord = int(line[3])

            for gate in netlist[net_id]:

                print("gate {} is connected to net {}".format(gate, net_id))

                # (-1) * x position * weight
                if char == 'x':
                    b[gate-GATE_ARR_OFFSET] = (-1) * x_coord * weights[net_id]

                elif char == 'y':
                    b[gate-GATE_ARR_OFFSET] = (-1) * y_coord * weights[net_id]

    f.close()

    return b
##################################################################################################

##################################################################################################
def main():

    # Get netlist
    netlist = get_netlist()            

    # Find number of gates
    num_gates = get_num_gates()

    # Get C matrix
    C = get_C(netlist, num_gates)

    # Get A matrix
    A = get_A(C) 

    # Get b_x
    b_x = get_b(C, 'x', netlist)
    print("\nb_x: \n{}\n".format(b_x))

    # Get b_y
    b_y = get_b(C, 'y', netlist)
    print("\nb_y: \n{}\n".format(b_y))

    # Solve quadratic placement using these matrices
    A = coo_matrix(A)
    
    # Ax = -b_x
    for i in range(0, len(b_x)):
        b_x[i] *= -1
    x = spsolve(A.tocsr(), b_x)

    # Ay = -b_y
    for i in range(0, len(b_y)):
        b_y[i] *= -1
    y = spsolve(A.tocsr(), b_y)

    # Visualize results of placement. Plot (x[i], y[i])
    # matplotlib.pyplot.scatter(x, y)
    # matplotlib.pyplot.show()

    print("x: \n{}".format(x))
    print("y: \n{}".format(y))
    

if __name__ == "__main__":
    main()

