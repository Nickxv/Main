import subprocess
import socket
import time
from mss import mss
import re

def get_ip_address():
    # Retrieve your phone's IP address
    result = subprocess.run(['adb', 'shell', 'ip', '-f', 'inet', 'address', 'show', 'wlan0'], capture_output=True)
    ip_address = "192.168.1.5"
    return ip_address.group(1) if ip_address else None

def screen_mirror(ip_address, port):
    with mss() as sct:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((ip_address, port))
            server_socket.listen(1)
            print(f"Waiting for a connection from {ip_address} on port {port}...")
            connection, client_address = server_socket.accept()

            try:
                print(f"Connection from {client_address}")

                while True:
                    # Capture the screen
                    screenshot = sct.shot(output='fullscreen.png')

                    # Send the screenshot to the client
                    with open('fullscreen.png', 'rb') as file:
                        data = file.read()
                        connection.sendall(data)

                    time.sleep(1)  # Adjust the delay as needed

            finally:
                connection.close()

if __name__ == "__main__":
    ip_address = get_ip_address()
    if ip_address:
        print(f"Found IP address: {ip_address}")

        port = 5555  # You can use any available port
        screen_mirror(ip_address, port)
    else:
        print("Unable to retrieve IP address. Make sure your device is connected and ADB is properly set up.")
