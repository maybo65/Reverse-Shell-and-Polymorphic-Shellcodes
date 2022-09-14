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


