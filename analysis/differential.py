import numpy as np

Sbox = [0x2, 0xd, 0x3, 0x9, 0x7, 0xb, 0xa, 0x6, 0xe, 0x0, 0xf, 0x4, 0x8, 0x5, 0x1, 0xc]

DDT = np.array([
[16,  0,  0,  0 , 0,  0 , 0 , 0 , 0 , 0 , 0  ,0  ,0  ,0  ,0 , 0],
[ 0,  0 , 0 , 0 , 0 , 0 , 0 , 0  ,0  ,0  ,2  ,2  ,4  ,4  ,2  ,2],
[ 0 , 4,  0,  0 , 4 , 0 , 0 , 0 , 0 , 4 , 0 , 0 , 0 , 4 , 0 , 0],
[ 0 , 4 , 0 , 0 , 4 , 0 , 0 , 0 , 0,  0,  2,  2 , 0 , 0 , 2 , 2],
[ 0 , 0,  0 , 0 , 0 , 4  ,4  ,0  ,2  ,2  ,0  ,0 , 0 , 0 , 2 , 2],
[ 0 , 0,  0,  4 , 0 , 4 , 0 , 0 , 2 , 2 , 2 , 2 , 0  ,0  ,0 , 0],
[ 0 , 2 , 2 , 0 , 2 , 0 , 0 , 2 , 2 , 0 , 0 , 2 , 2 , 0 , 0 , 2],
[ 0 , 2 , 2 , 0 , 2  ,0  ,0  ,2  ,2  ,0 , 2 , 0 , 2 , 0 , 2 , 0],
[ 0 , 0,  0 , 0 , 0 , 0 , 0 , 0  ,0  ,0  ,2,  2,  4 , 4 , 2,  2],
[ 0 , 0 , 4 , 4 , 0 , 0 , 4 , 4 , 0 , 0 , 0 , 0,  0,  0,  0,  0],
[ 0  ,0 , 2 , 2,  0,  0,  2,  2,  0,  4 , 0 , 0 , 0 , 4 , 0 , 0],
[ 0  ,0 , 2,  2,  0 , 0 , 2 , 2,  0,  0,  2,  2,  0 , 0 , 2,  2],
[ 0 , 0 , 4,  0,  0,  4,  0,  0 , 2  ,2  ,2  ,2 , 0 , 0 , 0 , 0],
[ 0,  0,  0,  0,  0,  4,  0,  4,  2,  2,  0 , 0 , 0 , 0 , 2,  2],
[ 0 , 2 , 0 , 2  ,2,  0,  2 , 0,  2,  0,  0 , 2 , 2 , 0 , 0 , 2],
[ 0,  2 , 0 , 2 , 2 , 0 , 2 , 0  ,2  ,0  ,2  ,0  ,2 , 0 , 2 , 0]], dtype=(int))

# LAT = np.array([
#  [ 8,  0,  0,  0,  0,  0 , 0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0 , 0],
#  [ 0,  0 ,-4 , 0 , 2 , 2 , 2 ,-2 , 0 ,-4  ,0  ,0 , 2 ,-2, -2, -2],
#  [ 0,  0,  0,  0 , 0 , 4 , 0 , 4 , 0 , 0 , 0 , 0 , 0 , 4 , 0 ,-4],
#  [ 0,  4,  0,  0 ,-2 ,-2 , 2 ,-2 , 0 , 0 ,-4 , 0 ,-2 , 2 ,-2 ,-2],
#  [ 0,  0,  0 , 0 , 0 , 0 , 0 , 0 , 0 , 4 , 0 , 4 , 4 , 0 ,-4 , 0],
#  [ 0,  0 ,-4  ,0 ,-2 ,-2 ,-2 , 2 , 0 , 0 , 0 ,-4 , 2 , 2 ,-2 , 2],
#  [ 0 , 4  ,0 ,-4 , 0 , 0  ,0  ,0  ,0  ,0,  0,  0 , 4 , 0 , 4 , 0],
#  [ 0 , 0 , 0 ,-4,  2, -2, -2 ,-2 , 0 , 0 , 4 , 0 ,-2 , 2 ,-2 ,-2],
#  [ 0 ,-2 ,-4, -2,  2,  0, -2 , 0 , 0 , 2 ,-4 , 2 ,-2 , 0,  2 , 0],
#  [ 0 , 2 , 0 , 2 , 0 , 2 ,-4 ,-2 , 4 ,-2 , 0 , 2 , 0 , 2 , 0 , 2],
#  [ 0 ,-2 , 0 , 2 ,-2,  0, -2, -4,  0,  2,  0, -2,  2,  0,  2 ,-4],
#  [ 0, -2,  0, -2,  0,  2,  4 ,-2 , 4 , 2 , 0 ,-2 , 0 , 2 , 0 , 2],
#  [ 0, -2 , 4 ,-2 , 2 , 0 ,-2 , 0 , 0 ,-2 ,-4 ,-2 , 2 , 0, -2,  0],
#  [ 0,  2,  0 , 2 , 4 ,-2 , 0 , 2 , 4 , 2 , 0 ,-2  ,0 ,-2 , 0, -2],
#  [ 0 , 2 , 0 ,-2 ,-2 , 4 ,-2 , 0 , 0 , 2 , 0 -2, -2 ,-4 ,-2 , 0],
#  [ 0,  2 , 0 , 2 , 4,  2,  0, -2 ,-4 , 2 , 0 ,-2 , 0 , 2 , 0 , 2]],dtype=(int))

row_matrix= np.array([
[1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
[0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1],
[0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]
], dtype=int)

def decimal_to_4bit_binary(num):
    return [(num >> 3) & 1, (num >> 2) & 1, (num >> 1) & 1, num & 1]

def circular_shift_left(row_matrix):
    return np.roll(row_matrix, -1)  


def compute_scalar_value(row_matrix, col_vector):
    and_result = np.bitwise_and(row_matrix, col_vector)
    scalar_value = np.bitwise_xor.reduce(and_result)    
    return scalar_value

def hex_to_4x32_matrix(hex_number):
    binary_string = bin(int(hex_number, 16))[2:].zfill(128)
    matrix = np.zeros((4, 32), dtype=int)
    for row in range(4):
        for col in range(32):
            matrix[row][col] = int(binary_string[row * 32 + col])

    return matrix

ct=0
def round_function(state,ct):
    for col_idx in range(state.shape[1]):
        column = state[:, col_idx]
        decimal_value = int(''.join(map(str, column)), 2)
        index = np.argmax(DDT[decimal_value])
        # sbox_value = Sbox[decimal_value]
        if index!=0:
            ct+=1
        new_column = decimal_to_4bit_binary(index)
        state[:, col_idx] = new_column

    # print(matrix_to_hex(state))
    print("number of active sboxes:" + str(ct))
    # state = hex_to_4x32_matrix("08100888280a088b081808092012200a")

    for row in range(4):
        first_row_column_vector = state[row, :]
        resultant_row_matrix = []
        current_row = row_matrix[row]
        for i in range(32):
            scalar_value = compute_scalar_value(current_row, first_row_column_vector)
            resultant_row_matrix.append(scalar_value)
            current_row = circular_shift_left(current_row)
        state[row, :] = resultant_row_matrix

    # print(matrix_to_hex(state))

def matrix_to_hex(matrix):
    flat_bits = matrix.flatten()
    binary_string = ''.join(map(str, flat_bits))
    hex_number = hex(int(binary_string, 2))[2:] 
    hex_number = hex_number.zfill(32)

    return hex_number



hex_string = input("Enter the hex string : \n")
m = hex_to_4x32_matrix(hex_string)

round_function(m,ct)


