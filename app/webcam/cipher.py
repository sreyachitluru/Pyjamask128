# cipher.py

# Define the constant key inside the cipher module
KEY = 0xA5  # example key (a random byte value)

substitution_key = KEY
reversed_substitution_key = KEY

def encrypt_file(input_file, output_file, KEY):
    """
    Encrypt or decrypt a file using XOR cipher with a constant key.
    """
    with open(input_file, 'rb') as f_in:
        data = f_in.read()

    # XOR the data with the constant key
    encrypted_decrypted_data = bytearray([byte ^ KEY for byte in data])

    with open(output_file, 'wb') as f_out:
        f_out.write(encrypted_decrypted_data)


def decrypt_file(input_file, output_file, KEY):
    """
    Encrypt or decrypt a file using XOR cipher with a constant key.
    """
    with open(input_file, 'rb') as f_in:
        data = f_in.read()

    # XOR the data with the constant key
    encrypted_decrypted_data = bytearray([byte ^ KEY for byte in data])

    with open(output_file, 'wb') as f_out:
        f_out.write(encrypted_decrypted_data)
