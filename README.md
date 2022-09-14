# Reverse-Shell-and-Polymorphic-Shellcodes
In this exercise I exploited a vulnerability on a **remote** machine  and achieved “Remote Code Execution” (RCE), and made the machine  connect back to me with a shell and wait for further instructions (“remote shell”).

In this exercise, we’ll attack a simple log server - a server that receives messages over the network and logs them to a file.

-   The server listens for incoming connections on a socket
    
-   From each connection it then reads 4 bytes for the length of the message, followed by the bytes of the string with the actual message 
-   The message must be \0 terminated

(Classic BOF candidate here😉)

# Attack motivation 
In the previous exercise (BOF), we exploited a vulnerability in a local process, to gain a privilege escalation - i.e. run with higher permissions. While this sort of attack is useful, typically we wish to attack remote machines.

# Part A
First, to prove there is actually a vulnerability in the server, we wish to find a message to send to the server so that it would crash.

Lets look as the server source code (at least some of it):
![image](https://user-images.githubusercontent.com/112778430/190275268-7f6a88f1-79f4-4e9a-9e37-311f86d7d232.png)

Lets notice the fact that the buffer which  going to hold the message is from size 1024. so, we are going to pad our message with 1000 chars of x\11. after that padding, we are going to add our malicious input, by adding to that AAABBBBCCCC...ZZZZ (A till Z four time each letter). meaning, that we are sending to the server a message with the payload \x00\x00\x04\x51\x11\x11....\x11\AAABBBBCCCC...ZZZZ. the first four bytes are indicating the length of the message (including the null terminator), and some big enough input that is going to make the server crash because of a buffer overflow.  
ok, cool so we can make it crash. what's next? 

## **Remote Shell Attack**
The attack we wish to carry is more or less the same as previous exercise (running exec with "/bin/sh"). But, opening a shell on a remote machine is pretty useless if we can’t control it. To use our shell, we’ll need to:

1.  Make the server open a socket to our C&C server
    
2.  Redirect STDIN, STDOUT and STDERR to the socket
    
3.  Only after these, we will run exec with /bin/sh 

### C&C servers
Now to the next question - where do we get a server for our C&C?

For this exercise, we will use the **netcat (nc) utility** - a program included with standard Linux distributions, which opens a socket and:
 

-   Prints to STDOUT what it receives from the socket
    
-   Reads from STDIN and sends that to the socket

Our C&C server will listen on **port 1337**

![image](https://user-images.githubusercontent.com/112778430/190276355-218dc332-b04b-4247-8b93-d2e1b30b513a.png)
. 
# Part B
In the python program (q2.py) , we are going to build a payload for a message that we will send to server, which going cause a buffer overflow, and then RCE. 

For that we'll need to write some assembly. we'll get that in a second, but lets take a look at our massage: 

**The message is going to look as so:**
*4 bytes indicating the leangth of our msg- in our case 1045* + *some_nop_padding* + *our assembly shell code* + *null terminator*.

lets dive in to the assembly shellcode:
![image](https://user-images.githubusercontent.com/112778430/190277272-897d90a9-e2f1-4379-b823-24362f72bec7.png)


1. First, we are going to take esp and move it right before our buffer. this will prevent some issues regarding the fact that the stack is going downward, and may override our code during the calls some functions. (btw- this actually took me about 2 hours to understand. I got weird behavior with my shellcode and couldn't understand why).
2. Then we are creating a new socket at the server side that is going to use as way to connect to our C&C server. for that, we are pushing to the stack the arguments, and calling the socket function, at adsress-0x8048730. We will get a socket fd from that, and will store it ecx. 
3. Now, we are going to call the connect function. The arguments are the the socketfd (which we got from the socket function, and is currently stored in ecx), pointer to socketadress struct (we'll get that in a second) and the address length. this is constant -0x10. we will push those onto the stack, and then call the connect function at address 0x08048750.

**about the socketadrdress struct**- this struct structure is as follows: first two bytes of sin_family (this is set to 0x2), and then 2 bytes of port we are going to use (also constant in our example, because we are going to connect to port 1337, which is 0x3905), and finally the address of the server we are going to connect to, as it was outputted from the init address function. After running the c code, I found out that for 127.0.0.1, this is going to be set to 0x100007F. 
So, now let's push those values, and by that create our socketadress struck on the stack.

4. Then, we are moving esp to ebx, which means that ebx is going to be the address of the struct we just built. 
5. After that, we are going call dup2, at address 0x8048600 3 times- one for stdin, one for stdout, and one for sdterr. for each of those, we are going to redirect them to our socketfd. This way, we can control the remote shell from our C&C server.
6. Finally, we are going to open a shell on the server, using a call to execv on address 0x80486D0. the arguments to those call: a pointer to the string /bin/sh and a pointer to an array of {/bin/sh, 0000}. This part is done in a similar way to our previous exercise (BOF). 

### How did I got those memory address? 
Those are the memory address of function I used and "relevant" memory addresses on the stack. 
using GDB and IDA, I could debug my core files causing by crashing the server (part A), and find all the relevant addresses on the stack and on the source code (this is also very similar to what I done in the BOF ex). 

### Small Tip:
you can write a c program that does what you want (like, connecting to a remote server), compile it, and then RE to see the assembly instructions and function you use and go on from there. This what I did here and it help a lot with the structs parts. 
















 



