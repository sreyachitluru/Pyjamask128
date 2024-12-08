# file_server.py

import socket
import os

def send_file(client_socket, file_path):
    """
    Send a file to the connected client.
    """
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        client_socket.send("File not found".encode())
        return

    # Send the file name
    file_name = os.path.basename(file_path)
    client_socket.send(file_name.encode())

    # Send the file data in chunks
    with open(file_path, 'rb') as f:
        while (file_data := f.read(1024)):
            client_socket.send(file_data)

    print(f"File {file_name} sent successfully.")

def start_server(host, port, file_path):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")
        send_file(client_socket, file_path)
        client_socket.close()

if __name__ == "__main__":
    start_server('localhost', 12345, 'encrypted_video.bin')  # Send the encrypted .bin file
