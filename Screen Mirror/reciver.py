import socket
from mss import mss
import cv2
import numpy as np

def start_receiver(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((ip, port))
        server_socket.listen()
        print(f"Receiver listening on {ip}:{port}")

        connection, client_address = server_socket.accept()

        with mss() as sct:
            while True:
                screenshot = sct.shot(output=None)

                # Read the screenshot image
                with open('screenshot.png', 'rb') as file:
                    screenshot_data = file.read()

                # Send the screenshot data to the sender
                connection.sendall(screenshot_data)

if __name__ == "__main__":
    host = '0.0.0.0'  # Use '0.0.0.0' to listen on all available interfaces
    port = 5555  # You can use any available port

    start_receiver(host, port)
