import socket
import select

class TcpServer:
    def __init__(self, host="0.0.0.0", port=2020):
        try:
            self.host = host
            self.port = port
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
        except Exception as e:
            print(f"Error creating TCP server: {e}")
            exit(1)

    def check_for_new_connection(self):
        # print("before : select")
        ready_to_read, _, _ = select.select([self.socket], [], [], 0.1)
        # print(f"ready_to_read : {ready_to_read}")
        if ready_to_read:
            client_socket, _ = self.socket.accept()
            data = self.handle_client(client_socket)
            return client_socket, data
        return None, None 
        
    def handle_client(self, client_socket: socket.socket):
        data = client_socket.recv(100).decode()
        # this is the response from the server
        # client_socket.send("".encode())
        return data
    
    def send_response(self, client_socket: socket.socket, res: str):
        client_socket.send(res.encode())
        client_socket.close()
        # ...

