import time
import requests
import subprocess
from cipher import encrypt_file, decrypt_file, substitution_key, reversed_substitution_key


# Step 1: Measure bandwidth
def measure_bandwidth(url="http://ipv4.download.thinkbroadband.com/5MB.zip"):
    print(f"Starting bandwidth measurement from {url}...")
    start_time = time.time()
    response = requests.get(url, stream=True)  # Using HTTP instead of HTTPS
    total_data = 0
    for chunk in response.iter_content(1024):  # Download in 1KB chunks
        total_data += len(chunk)
    elapsed_time = time.time() - start_time
    bandwidth = (total_data / elapsed_time) / 1e6  # Convert to Mbps
    print(f"Bandwidth measurement completed. Total data downloaded: {total_data / 1e6:.2f} MB")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Available bandwidth: {bandwidth:.2f} Mbps")
    return bandwidth

# Step 2: Select compression parameters based on bandwidth
def select_compression_params(bandwidth):
    print(f"Selecting compression parameters based on available bandwidth: {bandwidth:.2f} Mbps")
    if bandwidth > 10:  # High bandwidth
        print("High bandwidth detected. Choosing high bitrate and resolution.")
        return {"bitrate": "8M", "resolution": "1920x1080"}  # 1080p
    elif 5 < bandwidth <= 10:  # Medium bandwidth
        print("Medium bandwidth detected. Choosing moderate bitrate and resolution.")
        return {"bitrate": "4M", "resolution": "1280x720"}  # 720p
    else:  # Low bandwidth
        print("Low bandwidth detected. Choosing low bitrate and resolution.")
        return {"bitrate": "1M", "resolution": "854x480"}  # 480p

# Step 3: Compress video using VP9 codec (through FFmpeg)
def compress_video(input_file, output_file, bitrate, resolution):
    print(f"Starting video compression: Input file - {input_file}, Output file - {output_file}")
    print(f"Using VP9 codec with bitrate {bitrate} and resolution {resolution}")
    
    command = [
        "ffmpeg",
        "-i", input_file,               # Input file
        "-c:v", "libvpx-vp9",           # VP9 codec
        "-b:v", bitrate,                # Set bitrate
        "-s", resolution,               # Set resolution
        "-c:a", "libopus",              # Use Opus for audio codec (you can adjust this as needed)
        "-y",                           # Overwrite output file if exists
        output_file                     # Output file
    ]
    
    print("Executing FFmpeg command...")
    subprocess.run(command, check=True)
    print(f"Video compression completed. The compressed video is saved as: {output_file}")

# Main flow
if __name__ == "__main__":
    print("Starting the adaptive compression process...\n")
    
    print(f"Available Bandwidth: {measure_bandwidth():.2f} Mbps\n")
    
    bandwidth = measure_bandwidth()
    compression_params = select_compression_params(bandwidth)
    print(f"Selected Compression Parameters: {compression_params}\n")

    # Example video compression
    input_video = "input_video.mp4"  # Path to your input video file
    output_video = "output_video.webm"  # Path to save the compressed video
    compress_video(input_video, output_video, compression_params["bitrate"], compression_params["resolution"])
    

    input_video_file = "output_video.webm"  # The compressed video file
    binary_file = "video_binary.bin"  # The binary format of the video
    encrypted_file = "encrypted_video.bin"  # Encrypted binary file
    # decrypted_file = "decrypted_video.bin"  # Decrypted binary file
    # final_output_video = "final_output_video.webm"  # Final video after decryption

    # Step 1: Convert the compressed video into binary format
    print(f"Converting video {input_video_file} to binary format...")
    with open(input_video_file, 'rb') as f:
        video_binary_data = f.read()

    with open(binary_file, 'wb') as f:
        f.write(video_binary_data)
    print(f"Video converted and saved as {binary_file}")

    # Step 2: Encrypt the binary file
    encrypt_file(binary_file, encrypted_file, substitution_key)

    # Step 3: Decrypt the encrypted file
    # decrypt_file(encrypted_file, decrypted_file, reversed_substitution_key)

    # Step 4: Convert the decrypted binary back to video
    # with open(decrypted_file, 'rb') as f:
    #     decrypted_video_data = f.read()

    # with open(final_output_video, 'wb') as f:
    #     f.write(decrypted_video_data)
    # print(f"Decrypted video saved as {final_output_video}")
