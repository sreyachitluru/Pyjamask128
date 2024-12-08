# file_client.py

import socket
from cipher import encrypt_file, decrypt_file, substitution_key, reversed_substitution_key

def receive_file(client_socket):
    """
    Receive a file from the server and save it.
    """
    # Receive the file name
    file_name = client_socket.recv(1024).decode()
    if file_name == "File not found":
        print("File not found on the server.")
        return

    print(f"Receiving file: {file_name}")

    # Receive the file data and save it as encrypted .bin
    with open(file_name, 'wb') as f:
        while True:
            file_data = client_socket.recv(1024)
            if not file_data:
                break  # Stop receiving when no data is left
            f.write(file_data)

    print(f"File {file_name} received successfully.")

def start_client(server_host, server_port):
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    # Receive the encrypted file from the server
    receive_file(client_socket)

    # Now, decrypt the received file
    decrypt_file('encrypted_video.bin', 'decrypted_video.bin')

    # Convert the decrypted .bin file back to video
    bin_to_video('decrypted_video.bin', 'output_video.mp4')

    client_socket.close()

def bin_to_video(bin_file, output_video_file):
    """
    Convert a .bin file back to a video file.
    """
    with open(bin_file, 'rb') as f_in:
        bin_data = f_in.read()

    with open(output_video_file, 'wb') as f_out:
        f_out.write(bin_data)

if __name__ == "__main__":
    start_client('localhost', 12345)  # Server's host and port
