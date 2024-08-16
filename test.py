import socket
import threading

class Proxy:
    def __init__(self):
        self.username = 'username'
        self.password = 'password'
    
    def handle_client(self, connection):
        version, nmethods = connection.recv(2)
        
        methods = self.get_available_methods(nmethods, connection)
        
        if 2 not in set(methods):
            connection.close()
            return
        
        connection.sendall(bytes([SOCKS_VERSION, 2]))
        
        if not self.verify_credentials(connection):
            return 
        
        
            
    def get_available_methods(self, nmethods, connection):
        methods = []
        for i in range(nmethods):
            methods.append(ord(connection.recv(1)))
        return methods
    
    def run(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        
        while True:
            conn, addr = s.accept()
            print("* new connection from {}".format(addr))
            t = threading.Thread(target=self.handle_client, args=(conn,))
            t.start()

if __name__ == "__main__":
    proxy = Proxy()
    proxy.run("127.0.0.1", 12345)