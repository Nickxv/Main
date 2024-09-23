import cv2
import numpy as np
import pyautogui
import time
import ctypes
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

def mouse_click():
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # Left button down
    time.sleep(0.1)
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # Left button up

# Screen resolution
screen_width, screen_height = pyautogui.size()

# Video capture
cap = cv2.VideoCapture(0)

while True:
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS)

            tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y

            screen_x = int(tip_x * screen_width)
            screen_y = int(tip_y * screen_height)

            # Move the mouse
            pyautogui.moveTo(screen_x, screen_y)

    # Show the image
    cv2.imshow('MediaPipe Hands', image)

    # Break loop with q key
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
