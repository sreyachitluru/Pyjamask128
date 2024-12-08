import os
import tkinter as tk
from tkinter import messagebox, filedialog
from client import start_client
import subprocess

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Receiver Client")

        # Server Details
        tk.Label(root, text="Server Hostname:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.server_host = tk.Entry(root, width=30)
        self.server_host.insert(0, "localhost")  # Default value
        self.server_host.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(root, text="Server Port:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.server_port = tk.Entry(root, width=30)
        self.server_port.insert(0, "12345")  # Default value
        self.server_port.grid(row=1, column=1, padx=10, pady=5)

        # Action Buttons
        self.connect_button = tk.Button(root, text="Connect and Receive File", command=self.connect_to_server)
        self.connect_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.play_button = tk.Button(root, text="Play Video", command=self.play_video, state="disabled")
        self.play_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Status
        self.status_label = tk.Label(root, text="Status: Waiting for user action.", fg="blue")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)

        # Paths
        self.decrypted_video = "output_video.mp4"

    def connect_to_server(self):
        """
        Connect to the server, receive the encrypted file, decrypt it, and save it as a video.
        """
        host = self.server_host.get()
        port = self.server_port.get()

        # Validate Port
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Invalid Input", "Server port must be a number.")
            return

        self.status_label.config(text="Connecting to server...", fg="orange")
        self.root.update_idletasks()

        try:
            # Start the client to connect and receive the file
            start_client(host, port)

            # Check if the decrypted video is created
            if os.path.exists(self.decrypted_video):
                self.status_label.config(text=f"File received and decrypted: {self.decrypted_video}", fg="green")
                self.play_button.config(state="normal")  # Enable the Play button
            else:
                self.status_label.config(text="Decryption failed. File not received properly.", fg="red")

        except ConnectionRefusedError:
            self.status_label.config(text="Failed to connect to the server.", fg="red")
            messagebox.showerror("Connection Error", "Could not connect to the server. Please check the hostname and port.")
        except Exception as e:
            self.status_label.config(text="An error occurred.", fg="red")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def play_video(self):
        """
        Play the decrypted video using the default video player.
        """
        if not os.path.exists(self.decrypted_video):
            messagebox.showerror("File Not Found", "Decrypted video file not found.")
            return

        self.status_label.config(text=f"Playing video: {self.decrypted_video}", fg="blue")
        try:
            # Use ffplay to play the video
            subprocess.run(["ffplay", "-autoexit", self.decrypted_video], check=True)
        except FileNotFoundError:
            messagebox.showerror("Player Not Found", "ffplay is not installed. Please install FFmpeg to play the video.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while playing the video: {e}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
