import socket
import threading

def start_proxy_server(host, port):
    proxy_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #proxy_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse
    proxy_server_socket.bind((host, port))
    proxy_server_socket.listen(5)
    print(f"Proxy server listen on {host}:{port}")
    
    while True:
        client_socket, address = proxy_server_socket.accept()
        print(f"Connection from {address[0]}:{address[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
    
def handle_client(client_socket):
    try:    
        #Get all request from client
        request = b""
        while True:
            part = client_socket.recv(1024)
            request += part
            if len(part) < 1024:
                break
        print(f"\n---------------\nRequest from client:\n{request.decode('utf-8', errors='ignore')}---------------\n")
        #Handle request from client
        request_lines = request.split(b'\n')
        if len(request_lines) < 1:
            client_socket.close()
            return
        
        request_line_1st = request_lines[0].split()
        if len(request_line_1st) < 2:
            client_socket.close()
            return
        print(request_line_1st)
        
        url = request_line_1st[1]
        method = request_line_1st[0]
        #Check request whether GET
        if method == b'GET':
            handle_http_request(client_socket, url, request)
        elif method == b'POST':
            print("*********")
            print("POST Request")
            handle_http_request(client_socket, url, request)
            print("**********")
        elif method == b'CONNECT':
            print("**HTTPS REQUEST**")
            handle_https_request(client_socket, url, request)
        else:
            print("*********")
            print("Not support another request")
            print("*********")
            client_socket.close()
            
        client_socket.close()
    except: 
        client_socket.close()

def handle_https_request(client_socket, url, request):
    # Tách các dòng
    lines = request.split(b'\r\n')
    
    # Lấy dòng CONNECT
    connect_line = lines[0] 
    
    # Tách dòng CONNECT thành các phần
    _, target, _ = connect_line.split(b' ', 2)
    
    # Tìm dòng Host
    host_line = next(line for line in lines if line.startswith(b'Host:'))
    
    # Tách dòng Host
    _, host = host_line.split(b':', 1) 
    
    # Tách target thành webserver và port
    if b':' in target:
        webserver, port = target.rsplit(b':', 1)
        webserver = webserver.decode('utf-8')
        port = int(port.decode('utf-8'))
    else:
        webserver = target.decode('utf-8')
        port = 443  # Mặc định cho HTTPS
    
    print(f"Connecting to: {webserver}:{port}")
    
    # Kết nối đến máy chủ đích
    try:
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_socket.connect((webserver, port))
        
        # Gửi phản hồi kết nối thành công về client
        client_socket.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        
        # Chuyển tiếp dữ liệu giữa client và máy chủ đích
        def forward(source, destination):
            while True:
                try:
                    data = source.recv(4096)
                    if not data:
                        break
                    destination.sendall(data)
                    print(data)
                except socket.error as e:
                    print(f"Socket error during forwarding: {e}")
                    break
        
        client_to_server = threading.Thread(target=forward, args=(client_socket, proxy_socket))
        server_to_client = threading.Thread(target=forward, args=(proxy_socket, client_socket))
        
        client_to_server.start()
        server_to_client.start()
        
        client_to_server.join()
        server_to_client.join()
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        client_socket.close()
        proxy_socket.close()
    
def handle_http_request(client_socket, url, request):
    try:
       print(url)
       #Find webserver
       http_pos = url.find(b'://')
       temp = url[(http_pos+3):] if http_pos != -1 else url
       port_pos = temp.find(b':')
       webserver_pos = temp.find(b'/')
       webserver_pos = len(temp) if webserver_pos == -1 else webserver_pos
       print(webserver_pos)
       print(port_pos)
       #Find webserver and port
       webserver = temp[:(port_pos if port_pos != -1 else webserver_pos)]
       port = int(temp[(port_pos+1):webserver_pos]) if port_pos != -1 else 80
       print(webserver)
       print(port)
       proxy_server_handle(client_socket, webserver, port, request)
    except:
        client_socket.close()
        
def proxy_server_handle(client_socket, webserver, port, request):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.connect((webserver, port))
    print("Request: " + str(request.decode('utf-8', errors='ignore')))
    proxy_socket.sendall(request)
    
    #Get response from server
    while True:
        response = proxy_socket.recv(4096)
        if len(response) > 0:
            print("Response:\n" + str(response.decode('utf-8', errors='ignore')))
            client_socket.send(response)
        else:
            break
        
    proxy_socket.close()
    client_socket.close()
    
if __name__ == "__main__":
    start_proxy_server('127.0.0.1', 12345)