import cv2

def video_to_images(video_path, output_folder):
    """Converts an MP4 video to a series of JPG images."""

    # Create the output folder if it doesn't exist
    import os
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the video file
    vidcap = cv2.VideoCapture(video_path)

    # Read the frames and save them as JPG images
    success, image = vidcap.read()
    count = 0
    while success:
        cv2.imwrite(f"{output_folder}/frame{count:04d}.jpg", image)
        success, image = vidcap.read()
        count += 1

if __name__ == "__main__":
    video_path = "2025 FIRST Robotics Competition REEFSCAPE presented by Haas Game Animation [YWbxcjlY9JY].mp4"  # Replace with your video file path
    output_folder = "images"
    video_to_images(video_path, output_folder)