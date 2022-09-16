#! /usr/bin/env python3

import os
import socket
import struct
import sys


HOST = '127.0.0.1'
PORT = 8000


def network_order_uint32(value) -> bytes:
    return struct.pack('>L', value)


def get_payload(message: str):
    if message[-1] != '\0':
        message = message + '\0'
    # Convert from string to bytes
    message = message.encode('latin1')
    return network_order_uint32(len(message)) + message


def main(message: str):
    payload = get_payload(message)
    conn = socket.socket()
    conn.connect((HOST, PORT))
    try:
        conn.sendall(payload)
    finally:
        conn.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('USAGE: %s <message>' % os.path.basename(sys.argv[0]))
        sys.exit(1)
    main(message=sys.argv[1])
