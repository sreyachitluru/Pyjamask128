import numpy as np

state = np.ones((4,32),dtype=int)
Sbox = [0x2, 0xd, 0x3, 0x9, 0x7, 0xb, 0xa, 0x6, 0xe, 0x0, 0xf, 0x4, 0x8, 0x5, 0x1, 0xc]

row_matrix= np.array([
[1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
[0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1],
[0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]
], dtype=int)


# M0 = cir ([1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0]) ,
# M1 = cir ([0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1]) ,
# M2 = cir ([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1]) ,
# M3 = cir ([0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]) .

# Setting up the plaintexts
# giving the first column the all property and the rest as constant, 16 plaintexts 
# Create a list to hold the 16 matrices
matrices = []

# Generate 16 matrices
for num in range(16):
    # Create a 4x32 matrix filled with ones
    matrix = np.ones((4, 32), dtype=int)
    
    # Convert the number to a 4-bit binary representation
    binary_rep = [int(bit) for bit in format(num, '04b')]
    
    # Set the first column to the binary representation
    for row in range(4):
        matrix[row][0] = binary_rep[row]
    
    # Append the matrix to the list
    matrices.append(matrix)

def decimal_to_4bit_binary(num):
    return [(num >> 3) & 1, (num >> 2) & 1, (num >> 1) & 1, num & 1]

def circular_shift_left(row_matrix):
    return np.roll(row_matrix, -1)  


def compute_scalar_value(row_matrix, col_vector):
    and_result = np.bitwise_and(row_matrix, col_vector)
    scalar_value = np.bitwise_xor.reduce(and_result)    
    return scalar_value

def round_function(state,key):
    #adding the roundkey
    state = np.bitwise_xor(state, key)
    for col_idx in range(state.shape[1]):
        column = state[:, col_idx]
        decimal_value = int(''.join(map(str, column)), 2)
        sbox_value = Sbox[decimal_value]
        new_column = decimal_to_4bit_binary(sbox_value)
        state[:, col_idx] = new_column

    for row in range(4):
        first_row_column_vector = state[row, :]
        resultant_row_matrix = []
        current_row = row_matrix[row]
        for i in range(32):
            scalar_value = compute_scalar_value(current_row, first_row_column_vector)
            resultant_row_matrix.append(scalar_value)
            current_row = circular_shift_left(current_row)
        state[row, :] = resultant_row_matrix

    return state


def hex_to_4x32_matrix(hex_number):
    binary_string = bin(int(hex_number, 16))[2:].zfill(128)
    matrix = np.zeros((4, 32), dtype=int)
    for row in range(4):
        for col in range(32):
            matrix[row][col] = int(binary_string[row * 32 + col])

    return matrix


dummy_key = np.array([
[1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
[0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1],
[0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]
], dtype=int)

result = [None]*16
ct=0
cnst=0
for i in range(16):
    result[i] = round_function(matrices[i],dummy_key)


for row in range(4):
    for column in range(32):
        if row_matrix[row][column]==1:
            xor = 0
            for i in range(16):
                xor^=result[i][row][column]
            if xor==0:
                # print("Balanced property verified!")
                ct+=1
        else:
            # print("Constant property verified!")
            cnst+=1


print(cnst,ct)


