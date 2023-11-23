import socket
import cv2
import numpy as np
from mss import mss

def start_sender(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((ip, port))

        while True:
            # Receive the screenshot data from the receiver
            screenshot_data = client_socket.recv(4096)

            if not screenshot_data:
                break

            # Display the received screenshot
            nparr = np.frombuffer(screenshot_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imshow('Screen Mirror', img)

            # Close the window when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

if __name__ == "__main__":
    receiver_ip = '192.168.128.199'  # Replace with the IP address of the receiver
    receiver_port = 5555  # Use the same port as in the receiver script

    start_sender(receiver_ip, receiver_port)
