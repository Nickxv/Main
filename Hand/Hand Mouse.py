import pyautogui
import cv2
import numpy as np
import time
import subprocess
import ctypes

def mouse_click():
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # Left button down
    time.sleep(0.1)  # Adjust the delay according to your preference
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # Left button up
    
# Set the resolution of the screen (adjust according to your laptop's screen)
screen_width, screen_height = 1920, 1080  # Adjusted for a 17-inch laptop

# Create a VideoCapture object
cap = cv2.VideoCapture(1)

# Define the range of skin color in HSV
lower_skin = np.array([0, 20, 70], dtype=np.uint8)
upper_skin = np.array([20, 255, 255], dtype=np.uint8)

# Flag to track if a click has been performed
clicked = False

# Flag to track if finger tap gesture is in progress
tap_in_progress = False

# Tap duration in seconds
tap_duration = 0.1

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Convert the frame from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Extract skin color region
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour
        max_contour = max(contours, key=cv2.contourArea)

        # Get the area of the largest contour
        contour_area = cv2.contourArea(max_contour)

        # Perform finger tap if contour area is below a certain threshold
        if contour_area < 1000:  # Adjust threshold as needed
            if not tap_in_progress:
                tap_in_progress = True
                start_time = time.time()
        else:
            if tap_in_progress:
                if time.time() - start_time >= tap_duration:
                    pyautogui.mouseDown()
                    time.sleep(0.1)  # Adjust the delay according to your preference
                    pyautogui.mouseUp()
                    tap_in_progress = False

        # Get the centroid of the largest contour
        M = cv2.moments(max_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Move the mouse
            pyautogui.moveTo(cx * screen_width // cap.get(3), cy * screen_height // cap.get(4))

    cv2.imshow('Gesture Control', frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
mouse_click()
cap.release()
cv2.destroyAllWindows()
