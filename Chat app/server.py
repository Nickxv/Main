import socket
import threading

def handle_client(client_socket, address):
    print(f"Accepted connection from {address}")
    
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        
        # Broadcast the received message to all connected clients
        message = f"{address}: {data.decode('utf-8')}"
        print(message)
        broadcast(message)

    client_socket.close()
    print(f"Connection from {address} closed")

def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            clients.remove(client)

# Setup server
host = '127.0.0.1'
port = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

print(f"Server listening on {host}:{port}")

clients = []

while True:
    client_socket, address = server.accept()
    clients.append(client_socket)
    
    client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
    client_handler.start()
