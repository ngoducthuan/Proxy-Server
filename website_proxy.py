import socket 

def start_proxy_server(host, port):
    #Creaat a TCP socket
    proxy_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_server_socket.bind((host, port))
    proxy_server_socket.listen(5)
    print(f"Proxy server listening on {host}:{port}")
    
    while True:
        #Receive connect from client
        client_socket, client_address = proxy_server_socket.accept()
        print(f"Connect from {client_address}")
        handle_client(client_socket)

def handle_client(client_socket):
    request = client_socket.recv(1024)
    print(f"Request received: {request}")
    #Assuming request format is METHOD URL HTTP/1.1
    request_line = request.split(b'\n')
    
    url = request_line[0].split()[1]
    
    #Parse the URL to extract the host and port
    http_pos = url.find(b'://')
    if http_pos == -1:
        temp = url
    else:
        temp = url[(http_pos+3):]
    
    port_pos = temp.find(b':')
    
    #Find end of webserver
    webserver_pos = temp.find(b'/')
    if webserver_pos == -1:
        webserver_pos = len(temp)
    
    webserver = ""
    port = -1
    if (port_pos == -1 or webserver_pos < port_pos):
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]
    
    proxy_server_handle(webserver, port, client_socket, request)

def proxy_server_handle(webserver, port, client_socket, request):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.connect((webserver, port))
    print("Request: "+str(request))
    proxy_socket.sendall(request)
    
    while True:
        response = b""
        while True:
            chunk = proxy_socket.recv(4096)
            if not chunk:
                break
            response += chunk
        
        print("Response: " + str(response.decode('utf-8', errors='ignore')))
        if len(response.decode('utf-8', errors='ignore')) > 0:
            client_socket.send(response)
        else:
            break
    
    proxy_socket.close()
    client_socket.close()
    
if __name__ == "__main__":
    start_proxy_server('127.0.0.1', 12345)