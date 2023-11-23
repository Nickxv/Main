import socket
import threading
from tkinter import Tk, Frame, Scrollbar, Listbox, Entry, Button, END

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat App")

        self.chat_frame = Frame(root)
        self.chat_frame.pack(pady=10)

        self.scrollbar = Scrollbar(self.chat_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.message_list = Listbox(self.chat_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.message_list.pack(side="left", fill="both")
        self.scrollbar.config(command=self.message_list.yview)

        self.entry_field = Entry(root, width=30)
        self.entry_field.pack(pady=10)

        self.send_button = Button(root, text="Send", command=self.send_message)
        self.send_button.pack()

        # Connect to the server
        self.server_host = '127.0.0.1'
        self.server_port = 12345

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_host, self.server_port))

        # Start a separate thread to receive messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def send_message(self):
        message = self.entry_field.get()
        if message:
            self.client_socket.send(message.encode('utf-8'))
            self.entry_field.delete(0, END)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.message_list.insert(END, message)
            except OSError:
                break

if __name__ == "__main__":
    root = Tk()
    chat_client = ChatClient(root)
    root.mainloop()
