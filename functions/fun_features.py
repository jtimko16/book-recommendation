import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from typing import Tuple


# Function to load all images from a folder
def load_images_from_folder(folder_path: str) -> list[Tuple[str, np.ndarray]]:
    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    # Filter only image files (you can adjust the extension filter as needed)
    image_files = [
        f
        for f in files
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))
    ]

    images = []
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        # Load the image without resizing
        image = cv2.imread(image_path)

        if image is not None:  # Check if the image was loaded 
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            images.append((image_file, image))
        else:
            print(f"Failed to load {image_file}")

    return images


def extract_dominant_color(image: np.ndarray, k: int = 1) -> np.ndarray:
    # Convert image to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Reshape the image to a list of pixels
    pixels = hsv.reshape((-1, 3))

    # Apply K-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(
        np.float32(pixels), k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )

    # Extract the dominant color (in HSV space)
    dominant_color = centers[0]  # In HSV
    return dominant_color


# Function to infer the mood based on color
def infer_mood_from_color(dominant_color: np.ndarray) -> str:
    hue = dominant_color[0]
    saturation = dominant_color[1]
    value = dominant_color[2]

    # Convert hue from OpenCV's 0-180 range to 0-360 degrees
    hue *= 2

    # General mood classification
    if hue < 60 or hue >= 300:  # Reds
        mood = "Energetic"
    elif hue < 180:  # Greens and Yellows
        mood = "Calm"
    else:  # Blues and Purples
        mood = "Mysterious"

    # Adjust mood based on brightness
    if value < 80:
        mood += " and dark"
    elif value > 200:
        mood += " and bright"

    # Adjust mood based on saturation
    mood += " with muted colors" if saturation < 50 else " with saturated colors"

    return mood


# Function to plot the dominant color (for visual inspection)
def plot_dominant_color(dominant_color: np.ndarray) -> None:
    # Convert HSV to RGB for display purposes
    rgb_color = cv2.cvtColor(np.uint8([[dominant_color]]), cv2.COLOR_HSV2BGR)[0][0]
    plt.imshow([[rgb_color]])
    plt.axis("off")
    plt.show()


# Main function to process the image and extract features
def process_book_cover(image: np.ndarray, verbosity: int = 0)-> Tuple[np.ndarray, str]:
    # Extract dominant color
    dominant_color = extract_dominant_color(image)

    # Infer mood based on dominant color
    mood = infer_mood_from_color(dominant_color)

    if verbosity > 0:
        plot_dominant_color(dominant_color)
        # Print extracted features and mood inference
        print(f"Dominant Color (HSV): {dominant_color}")
        print(f"Inferred Mood: {mood}")

    return dominant_color, mood
