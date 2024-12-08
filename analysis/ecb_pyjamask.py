import numpy as np

Sbox = [0x2, 0xd, 0x3, 0x9, 0x7, 0xb, 0xa, 0x6, 0xe, 0x0, 0xf, 0x4, 0x8, 0x5, 0x1, 0xc]
row_matrix= np.array([
    
[1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
[0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1],
[0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]
], dtype=int)

key_cir_matrix = np.array([1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0], dtype=int)
round_constant = [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0]
M = np.array([
    [0,1,1,1],
    [1,0,1,1],
    [1,1,0,1],
    [1,1,1,0]
], dtype=int)

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


def key_schedule_round(master, i):
    master_key = master.copy()  # Ensure we don't modify the input directly
    for col_idx in range(master_key.shape[1]):
        column = master_key[:, col_idx]
        master_key[:, col_idx] = np.dot(M, column)  # Corrected matrix-vector multiplication
    
    first_row_column_vector = master_key[0, :]
    resultant_row_matrix = []
    current_row = key_cir_matrix
    for _ in range(32):  # Ensure exactly 32 iterations
        scalar_value = compute_scalar_value(current_row, first_row_column_vector)
        resultant_row_matrix.append(scalar_value)
        current_row = circular_shift_left(current_row)

    # Ensure `resultant_row_matrix` is an array of shape (32,)
    resultant_row_matrix = np.array(resultant_row_matrix, dtype=int)
    master_key[0, :] = resultant_row_matrix

    master_key[1, :] = np.roll(master_key[1, :], -8)
    master_key[2, :] = np.roll(master_key[2, :], -15)
    master_key[3, :] = np.roll(master_key[3, :], -18)

    cnst = decimal_to_4bit_binary(i)  # Use the helper function

    master_key[3, 0:8] = np.bitwise_xor(master_key[3, 0:8], round_constant[0:8])
    master_key[2, 8:16] = np.bitwise_xor(master_key[2, 8:16], round_constant[8:16])
    master_key[1, 16:24] = np.bitwise_xor(master_key[1, 16:24], round_constant[16:24])
    master_key[0, 24:28] = np.bitwise_xor(master_key[0, 24:28], round_constant[24:28])
    master_key[0, 28:32] = np.bitwise_xor(master_key[0, 28:32], cnst)

    return master_key



    

def key_schedule(master):
    round_keys=[master]
    for i in range(13):
        round = key_schedule_round(master,i+1)
        round_keys.append(round)
    return round_keys

def pyjamask(state,key):
    plaintext = state.copy()
    round_keys = [None]*14
    round_keys = key_schedule(key)
    for i in range(14):
        plaintext = round_function(plaintext,round_keys[i])
    return plaintext

def ecb_pyjamask(state,key):
    binary_string = bin(state)[2:]
    if len(binary_string) % 128 != 0:
        padding_length = 128 - (len(binary_string) % 128)
        binary_string = '0' * padding_length + binary_string
    ciphertext = []
    for i in range(0, len(binary_string), 128):
        chunk = binary_string[i:i + 128]  
        bit_array = np.array([int(bit) for bit in chunk], dtype=int)
        matrix = bit_array.reshape((4, 32))
        ciphertext.append(pyjamask(matrix,key))

    concatenated_bits = []
    for matrix in ciphertext:
        flattened_bits = matrix.flatten()
        concatenated_bits.extend(flattened_bits)
    binary_str = ''.join(map(str, concatenated_bits))
    decimal_value = int(binary_str, 2)
    
    return decimal_value


# def decrypt_round(state,key):






#give any decimal value as input
state = 12344444432343435454545445
dummy = np.array([
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
], dtype=int)

    
print(ecb_pyjamask(state,dummy))



