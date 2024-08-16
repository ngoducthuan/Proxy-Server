import socket
import sys
import threading

HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or "." for i in range(256)])
#print(HEX_FILTER)

#Covert String to Hexdump
def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()
    
    result = list()

    for i in range(0, len(src), length):
        word = str(src[i:i+length])
        print(word)
        printable = word.translate(HEX_FILTER)
        #Using ord function to convert character to present number.
        hex = ' '.join([f'{ord(c):02X}' for c in word])
        hex_width = length*3
        result.append(f'{i:04X}    {hex:<{hex_width}}     {printable}')
    
    if show:
        for line in result:
            print(line)
    else:
        return result

#Receive data
def receive_from(connection):
    buffer = b""
    connection.settimeout(30)
    try:
        while True:
            data = connection.recv(4096)
            print("Data: "+data)
            if not data:
                break
            buffer += data
    except Exception as e:
        print("Error receive_from() function")
        pass

    return buffer

#Handle request from client
def request_handler(buffer):
    return buffer

#Handle response to client
def response_handler(buffer):
    return buffer

#Proxy handle
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Create a connect from proxy to remote server
    remote_socket.connect((remote_host, remote_port))
    
    print("Receive first: "+str(receive_first))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
    
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        print("OKe1")
        client_socket.send(remote_buffer)
        print("Oke2")

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] Receive %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")
        
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost")
        
        if not len(local_buffer) or not len(local_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Close connections.")
            break
#
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(local_host + " "+str(local_port))
        print('problem on bind %r' % e)

        print("[!!] Failed to listen on %s:%d" %(local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)    

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        #Print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        #Start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [local_host] [local_port]", end='')
        print("[remote_port] [remote_port] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == "__main__":
    main()