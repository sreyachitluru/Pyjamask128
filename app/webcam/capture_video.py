import subprocess
import threading
import time
from cipher import encrypt_file, substitution_key  # Your custom encryption method

def capture_video_frame(device='/dev/video0', duration=10, fps=20, output_video='input_video.mp4', bin_file='video_binary.bin', encrypted_file='encrypted_video.bin'):
    """
    Capture video from webcam using v4l2, save to video and binary file, then encrypt the binary data.
    
    Args:
        device (str): Path to the webcam device (usually '/dev/video0').
        duration (int): Duration of video capture in seconds.
        fps (int): Frames per second.
        output_video (str): Name of the output video file.
        bin_file (str): Output binary file.
        encrypted_file (str): Encrypted output file.
    """
    # Start ffmpeg process to capture video to file
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'v4l2',               # Video for Linux 2 (v4l2) capture device
        '-framerate', str(fps),     # Frame rate
        '-video_size', '640x480',   # Video resolution (change as needed)
        '-i', device,               # Device path
        '-c:v', 'libx264',          # Video codec
        '-pix_fmt', 'yuv420p',      # Pixel format
        output_video                # Output video file
    ]
    
    # Start ffmpeg process
    ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Capturing video from {device} for {duration} seconds...")

    # Run the capture process for the given duration
    time.sleep(duration)
    
    # Terminate the ffmpeg process after capturing
    ffmpeg_process.terminate()
    print(f"Video capture complete. Video saved as {output_video}")

    # Start the binary conversion and encryption in parallel after the capture is done
    def convert_and_encrypt():
        """
        Convert the captured video to binary format and encrypt it in real-time.
        """
        print(f"Converting video {output_video} to binary and encrypting...")
        
        # Use distinct variable names for the video and binary file
        with open(output_video, 'rb') as video_file, open(bin_file, 'wb') as binary_file:
            binary_file.write(video_file.read())
        
        print(f"Video saved as binary in {bin_file}")
        
        # Encrypt the binary data after conversion
        encrypt_file(bin_file, encrypted_file, substitution_key)
        print(f"Encrypted file saved as {encrypted_file}")

    # Start the binary conversion and encryption thread
    encryption_thread = threading.Thread(target=convert_and_encrypt)
    encryption_thread.start()
    
    # Wait for the encryption thread to finish
    encryption_thread.join()
    print("Encryption process completed.")

# Example usage
capture_video_frame(device='/dev/video0', duration=3, fps=20, output_video='input_video.mp4', bin_file='video_binary.bin', encrypted_file='encrypted_video.bin')
