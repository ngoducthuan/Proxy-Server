import socket
import threading

def handle_https_request(client_socket, request):
    # Tách các dòng trong yêu cầu CONNECT
    lines = request.split(b'\r\n')
    
    # Lấy dòng CONNECT
    connect_line = lines[0]
    
    # Tách dòng CONNECT thành các phần
    _, target, _ = connect_line.split(b' ', 2)
    
    # Tìm dòng Host
    host_line = next(line for line in lines if line.startswith(b'Host:'))
    
    # Tách dòng Host
    _, host = host_line.split(b':', 1)
    host = host.strip()
    
    # Tách target thành webserver và port
    if b':' in target:
        webserver, port = target.rsplit(b':', 1)
        webserver = webserver.decode('utf-8')
        port = int(port.decode('utf-8'))
    else:
        webserver = target.decode('utf-8')
        port = 443  # Mặc định cho HTTPS
    
    print(f"Connecting to tesst: {webserver}:{port}")
    
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
                except socket.error as e:
                    print(f"Socket error during forwarding: {e}")
                    break
        
        # Tạo các thread để chuyển tiếp dữ liệu
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

def handle_client(client_socket):
    # Nhận yêu cầu từ client
    request = client_socket.recv(4096)
    if b'CONNECT' in request:
        handle_https_request(client_socket, request)
    else:
        print("Unsupported request type")
        client_socket.close()

def start_proxy():
    LISTEN_HOST = '127.0.0.1'
    LISTEN_PORT = 12345
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((LISTEN_HOST, LISTEN_PORT))
        server_socket.listen(5)
        print(f'Proxy server đang lắng nghe tại {LISTEN_HOST}:{LISTEN_PORT}')
        
        while True:
            client_socket, addr = server_socket.accept()
            print(f'Nhận kết nối từ {addr}')
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    start_proxy()