# main.py

from cipher import xor_encrypt_decrypt

def video_to_bin(video_file, bin_file):
    """
    Convert a video file to a .bin file.
    """
    with open(video_file, 'rb') as f_in:
        video_data = f_in.read()

    with open(bin_file, 'wb') as f_out:
        f_out.write(video_data)

def bin_to_video(bin_file, output_video_file):
    """
    Convert a .bin file back to a video file.
    """
    with open(bin_file, 'rb') as f_in:
        bin_data = f_in.read()

    with open(output_video_file, 'wb') as f_out:
        f_out.write(bin_data)

def main():
    # Convert video to bin
    video_to_bin('output_video.webm', 'input_video.bin')
    
    # Encrypt the .bin file
    xor_encrypt_decrypt('input_video.bin', 'encrypted_video.bin')
    
    # Decrypt the .bin file
    xor_encrypt_decrypt('encrypted_video.bin', 'decrypted_video.bin')
    
    # Convert the decrypted .bin back to video
    bin_to_video('decrypted_video.bin', 'output_video.mp4')

if __name__ == "__main__":
    main()
