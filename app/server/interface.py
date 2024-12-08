import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from bandwidth import measure_bandwidth, select_compression_params, compress_video, encrypt_file
from server import start_server
from cipher import encrypt_file, decrypt_file, substitution_key, reversed_substitution_key


class AdaptiveVideoInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Adaptive Video Transmission")
        self.root.geometry("600x400")

        # Video File Selection
        tk.Label(root, text="Select Input Video File:").pack(pady=10)
        self.input_file_entry = tk.Entry(root, width=50)
        self.input_file_entry.pack(pady=5)
        tk.Button(root, text="Browse", command=self.browse_input_file).pack(pady=5)

        # Status Display
        tk.Label(root, text="Process Status:").pack(pady=10)
        self.status_label = tk.Label(root, text="Waiting for user action.", fg="blue", wraplength=500, justify="center")
        self.status_label.pack(pady=10)

        # Action Buttons
        self.start_button = tk.Button(root, text="Start Process", command=self.start_process, bg="green", fg="white")
        self.start_button.pack(pady=20)

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_program, bg="red", fg="white")
        self.exit_button.pack(pady=10)

        # Other attributes
        self.bandwidth = 0
        self.compression_params = None
        self.compressed_video = "output_video.webm"
        self.binary_file = "video_binary.bin"
        self.encrypted_file = "encrypted_video.bin"
        self.server_host = "localhost"
        self.server_port = 12345

    def browse_input_file(self):
        """
        Open a file dialog to select an input video file.
        """
        file_path = filedialog.askopenfilename(
            title="Select Input Video File",
            filetypes=(("MP4 Video Files", "*.mp4"), ("All Files", "*.*"))
        )
        if file_path:
            self.input_file_entry.delete(0, tk.END)
            self.input_file_entry.insert(0, file_path)

    def update_status(self, message, color="blue"):
        """
        Update the status label with a new message.
        """
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()

    def measure_bandwidth(self):
        """
        Measure available bandwidth.
        """
        self.update_status("Measuring bandwidth...", "orange")
        self.bandwidth = measure_bandwidth()
        self.update_status(f"Measured bandwidth: {self.bandwidth:.2f} Mbps", "green")

    def compress_video(self):
        """
        Compress the input video based on the measured bandwidth.
        """
        input_video = self.input_file_entry.get()
        if not os.path.exists(input_video):
            self.update_status("Error: Input video file not found!", "red")
            return False

        self.update_status("Selecting compression parameters...", "orange")
        self.compression_params = select_compression_params(self.bandwidth)
        self.update_status(f"Selected compression parameters: {self.compression_params}", "green")

        self.update_status("Compressing the video...", "orange")
        compress_video(input_video, self.compressed_video, self.compression_params["bitrate"], self.compression_params["resolution"])
        self.update_status(f"Video compressed successfully: {self.compressed_video}", "green")
        return True

    def convert_to_binary_and_encrypt(self):
        """
        Convert the compressed video to binary and encrypt it.
        """
        self.update_status("Converting compressed video to binary format...", "orange")
        with open(self.compressed_video, "rb") as f:
            video_binary_data = f.read()

        with open(self.binary_file, "wb") as f:
            f.write(video_binary_data)
        self.update_status(f"Binary file saved: {self.binary_file}", "green")

        self.update_status("Encrypting the binary file...", "orange")
        encrypt_file(self.binary_file, self.encrypted_file, substitution_key)
        self.update_status(f"Encrypted file saved: {self.encrypted_file}", "green")

    def start_server(self):
        """
        Start the server to send the encrypted video file.
        """
        self.update_status("Starting the server to send the encrypted file...", "orange")
        server_thread = threading.Thread(target=start_server, args=(self.server_host, self.server_port, self.encrypted_file))
        server_thread.daemon = True
        server_thread.start()
        self.update_status(f"Server started on {self.server_host}:{self.server_port}", "green")

    def start_process(self):
        """
        Perform the entire adaptive video transmission process.
        """
        input_video = self.input_file_entry.get()
        if not input_video:
            self.update_status("Error: Please select an input video file.", "red")
            return

        try:
            self.measure_bandwidth()
            if not self.compress_video():
                return
            self.convert_to_binary_and_encrypt()
            self.start_server()
            self.update_status("Process completed. The server is now ready for client connections.", "green")
        except Exception as e:
            self.update_status(f"Error occurred: {str(e)}", "red")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def exit_program(self):
        """
        Exit the program.
        """
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AdaptiveVideoInterface(root)
    root.mainloop()