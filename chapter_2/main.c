#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <unistd.h> 
#include <string.h>
#include <netinet/in.h>
#include <sys/mman.h>
#include <arpa/inet.h>

#define MESSAGE_BUFFER_SIZE 1024
#define MESSAGE_END_BYTES "endfunc"

typedef unsigned char BYTE;

void input_key(char* prompt, BYTE* buf);
BYTE* op(BYTE* str);
int connect_to_socket_server();
void execute_code(void* funcs[], BYTE* buf);
int check_key(void* funcs[], BYTE* buf, BYTE* key);
int update_buffer_and_prompt(BYTE* buf, BYTE* prompt);
int receive_code(void* funcs[]);

int main()
{
    void* funcs[32] = {0};
    int result = receive_code(funcs);
    if (result < 0) {
        printf("Une erreur est survenue lors de la verification :(");
        exit(EXIT_FAILURE);
    }

    BYTE buf[16];
    BYTE key[16];
    char prompt[128];

    while (1)
    {
        int update = update_buffer_and_prompt(buf, prompt);
        if (update < 0) {
            printf("Une erreur est survenue lors de la verification :(");
            exit(EXIT_FAILURE);
        } else if (update == 1337)
        {
            printf("C'est bon, tu as bien mérité ton flag.. Envoie toutes les clés concaténées au serveur de vérification pour le recevoir.\n");
            break;
        }
        input_key(prompt, key);
        if (check_key(funcs, buf, key) != 0) {
            printf("Mauvaise clé, dommage..\n");
            exit(EXIT_FAILURE);
        }
    }

    return 0;
}

void input_key(char* prompt, BYTE* key)
{
    printf("%s", prompt);
    BYTE input[32];
    fgets(input, 32, stdin);
    memcpy(key, input, 16);
}

BYTE* op(BYTE* str) {
    BYTE * result = malloc(16);
    for (int i = 0; i < 16; i++) {
        BYTE c = str[i];//INSTRUCTIONS
		result[i] = c;
    }
    return result;
}

int connect_to_socket_server() {

    char* host;
    //HOST
    int port;
    //PORT

    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        printf("Impossible de se connecter au serveur..");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);
    serv_addr.sin_addr.s_addr = inet_addr(host);

    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        printf("Impossible de se connecter au serveur..");
        exit(EXIT_FAILURE);
    }

    char* token;
    //TOKEN
    
    // Send token to server
    send(sockfd, token, strlen(token), 0);

    return sockfd;
}

void execute_code(void* funcs[], BYTE* buf) {
    
    int i = 0;

    while (1)
    {
        void (*func)(BYTE*) = funcs[i];
        if (func == NULL) {
            break;
        }
        func(buf);
        i++;
    }
}

int check_key(void* funcs[], BYTE* buf, BYTE* key) {
    // printf("Got key: %s\n", key);
    execute_code(funcs, key);
    if (memcmp(key,op(buf), 16) == 0) {
        return 0;
    } else {
        return 1;
    }
}

int receive_func(int sockfd, char *buffer, size_t buffer_size) {
    char recv_buffer[MESSAGE_BUFFER_SIZE];
    size_t total_bytes_received = 0;
    ssize_t bytes_received;

    while (1) {
        bytes_received = recv(sockfd, recv_buffer, MESSAGE_BUFFER_SIZE, 0);
        if (bytes_received < 0) {
            return -1;
        } else if (bytes_received == 0) {
            break;
        }
        // Check if 'endmsg' is received
        memcpy(buffer + total_bytes_received, recv_buffer, bytes_received);
        total_bytes_received += bytes_received;
        
        char *endmsg_ptr = strstr(recv_buffer, MESSAGE_END_BYTES);

        if (endmsg_ptr != NULL) {
            break;
        }        
    }

    return total_bytes_received - strlen(MESSAGE_END_BYTES);
}

int update_buffer_and_prompt(BYTE* buf, BYTE* prompt) {
    int sockfd = connect_to_socket_server();

    ssize_t bytes_received = recv(sockfd, buf, 16, 0);
    if (bytes_received < 1) {
        return -1;
    }
    memset(prompt, 0, 128);
    bytes_received = recv(sockfd, prompt, 128, 0);
    if (bytes_received < 1) {
        return -1;
    }
    if (memcmp(prompt, "done", 4) == 0) {
        return 1337;
    }
    return 0;
}   

int receive_code(void* funcs[]) {

    int i = 0;

    while (1)
    {        
        char* buffer = malloc(MESSAGE_BUFFER_SIZE);        
        // Allocate executable buffer        
        void* exec_buffer = mmap(NULL, MESSAGE_BUFFER_SIZE, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

        if (buffer == MAP_FAILED) {
            return -1;
        }
        
        int sockfd = connect_to_socket_server();
        int result = receive_func(sockfd, buffer, MESSAGE_BUFFER_SIZE);
        close(sockfd);

        if (result < 0) {
            return -1;
        } else if (result == 0) {
            break;
        }
        
        // Write received data to executable buffer
        memcpy(exec_buffer, buffer, result);
        funcs[i] = exec_buffer;
        free(buffer);

        i++;
    }

    return 0;
}