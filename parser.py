import numpy as np

def get_C():
    f = open("place.tiny", "r")
    
    # Read placement grid rows/columns
    grid_dims = f.readline().replace('\n','').split(' ')

    # Keep track of net IDs and which gates are connected to each net ID (1-?)
    # First index represents the net ID and stores a list of gates connected to this net ID.
    netlist = [[] for y in range(int(grid_dims[1])-1)]

    print(netlist)

    # Initialize C matrix from grid dimensions
    C = [[0 for x in range(int(grid_dims[0])-1)] for y in range(int(grid_dims[1])-1)] 

    for line in f:
        if (line == "-1\n"):
            continue

        # Handle gate
        elif line.split(' ')[1] == 'g':
            line = line.replace('\n','').split(' ')
            num_connections = line[2]

            # Add each connection
            for i in range(0, int(num_connections)):
                print("net {} is connected to gate {}".format(line[i+3],line[0]))
                netlist[int(line[i+3])].append(int(line[0]))
                C[int(line[0])][int(line[i+3])] += 1
                C[int(line[i+3])][int(line[0])] += 1

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
                A[i][j] += C[i][j]
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

            # (-1) * x position * weight
            if char == 'x':
                b[int(line[4])] = (-1) * int(line[2])
            elif char == 'y':
                b[int(line[4])] = (-1) * int(line[3])

    f.close()
    return b

def main():
    # TODO: decompose multipoint nets into 2-point nets (see slides 8-10 of L13)
    C = get_C()                 # Get C matrix
    A = get_A(C)                # Get matrix A 
    b_x = get_b(C, 'x')         # Get b_x
    b_y = get_b(C, 'y')         # Get b_y

    # TODO: Solve quadratic placement using these matrices
    # x = np.linalg.solve(A, b_x)
    # y = np.linalg.solve(A, b_y)

    # TODO: Visualize results of placement

if __name__ == "__main__":
    main()

