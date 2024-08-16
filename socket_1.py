import socket
def handl_forward(query):
    target_host = "www.google.com"
    target_port = 80

    #User enter your query
    #query = input("Enter search query: ")

    #Encode the query to the URL endcode 
    query_encode = query.replace(" ","+")
    
    print("Query: "+str(query))
    
    try:
        #Creat a request with the search squery
        request = f"GET /search?q={query_encode} HTTP/1.1\r\nHost: google.com\r\nConnection: close\r\n\r\n"
        #Encode request
        request_bytes = request.encode("utf-8")
        
        print("[==>]Client send request to proxy." + "\n" + str(request))

        #Create a socket object 
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Connect the client
        client.connect((target_host, target_port))

        #Send some data
        client.send(request_bytes)
        print("[==>] Proxy sent request to remote.")

        #Receive some data
        response = client.recv(4096)

        client.close()
    except:
        client.close()
    
    return response

def proxy_listen():
    proxy_host = "127.0.0.1"
    proxy_port = 12345
    
    try:
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        proxy_socket.bind((proxy_host, proxy_port))
        proxy_socket.listen(5)
        
        print(f"[*] Listen on {proxy_host}:{proxy_port}")
        
        #Accept connect from local 
        client_local, address = proxy_socket.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        while True:    
            #Send request query from client
            client_local.send(b"=>> Enter your query: ")
            
            #Receive query from client
            query = client_local.recv(4096)
            #Decode query to string
            query = query.decode().strip()

            #Proxy handler
            response = handl_forward(query)       
            #print(response)
            print("[<==] Server sent response to proxy: "+"\n"+str(response.decode()))
            
            client_local.send(b"[*] Response:")
            client_local.send(response)
            
            print("[<==]Proxy sent response to client.")
        proxy_socket.close()
    except:
        proxy_socket.close()
    
if __name__ == "__main__":
    proxy_listen()