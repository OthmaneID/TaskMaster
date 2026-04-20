import socket
import select


class TcpClient:
    def __init__(self, host="0.0.0.0", port=2020):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
        except Exception as e:
            print(f"Error connecting to server (server may be down): {e}")
            exit(1)
        self.fds = [self.socket]

    def send(self, message:str):
        # ready_to_write, _, _ = select.select()
        try:
            message_bytes = message.encode()
            self.socket.send(message_bytes)
        except Exception as e:
            print(f"Error sending message: {e}")


    def receive(self) -> str:
        # first check if the server sent something
        ready_to_read, _, _ = select.select([self.socket], [], [], 5)
        if ready_to_read:
            data = self.socket.recv(1024).decode()
            ready_to_read.clear()
            while True:
                ready_to_read, _, _ = select.select([self.socket], [], [], 5)
                if ready_to_read:
                    chunk = self.socket.recv(1024).decode()
                    if not chunk:
                        break
                    data += chunk
                    
                else:
                    break
                ready_to_read.clear()
            return data
        else:
            print("Server is not ready to read")
            return ""
