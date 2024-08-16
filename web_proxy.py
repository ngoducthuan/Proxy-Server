import socket

def start_proxy_server(host, port):
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Proxy server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        handle_client(client_socket)

def handle_client(client_socket):
    request = b""
    while True:
        part = client_socket.recv(1024)
        request += part
        if len(part) < 1024:
            break

    print(f"Original request received: {request.decode('utf-8', errors='ignore')}")

    if b'GET' in request:
        handle_http_request(client_socket, request)
    else:
        print("Unsupported method or request")
        client_socket.close()

def handle_http_request(client_socket, request):
    # Extract URL from the request
    request_lines = request.split(b'\n')
    request_line = request_lines[0].split()
    if len(request_line) < 2:
        client_socket.close()
        return

    url = request_line[1]

    # Parse URL to extract the host and port
    http_pos = url.find(b'://')
    temp = url[(http_pos + 3):] if http_pos != -1 else url
    port_pos = temp.find(b':')
    webserver_pos = temp.find(b'/')
    webserver_pos = len(temp) if webserver_pos == -1 else webserver_pos

    webserver = temp[:port_pos if port_pos != -1 else webserver_pos]
    port = int(temp[(port_pos + 1):webserver_pos]) if port_pos != -1 else 80

    proxy_server_handle(webserver, port, client_socket, request)

def proxy_server_handle(webserver, port, client_socket, request):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.connect((webserver, port))
    print("Request being forwarded:")
    print(request.decode('utf-8', errors='ignore'))  # Print request for debugging

    proxy_socket.sendall(request)

    response_data = b""
    while True:
        chunk = proxy_socket.recv(4096)
        if not chunk:
            break
        response_data += chunk

    # Print part of the response for debugging (use safe decoding)
    try:
        print("Full response received:")
        print(response_data.decode('utf-8', errors='ignore'))  # Print response as text if possible
    except UnicodeDecodeError:
        print("Binary response received, cannot decode to text")

    # Send the full response to the client
    client_socket.sendall(response_data)

    proxy_socket.close()
    client_socket.close()

if __name__ == "__main__":
    start_proxy_server('127.0.0.1', 12345)
