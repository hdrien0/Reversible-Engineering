//Author : _hdrien
//404CTF 2024

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define BYTE unsigned char

BYTE * op(BYTE * str);

int main(int argc, BYTE * argv[]) {
    if (argc < 2) {
        printf("J'ai besoin d'un argument!\n");
        return 1;
    }
    int len = strlen(argv[1]);
    if (len != 16) {
        printf("L'argument doit comporter 16 caractères.\n");
        return 1;
    }

    BYTE buf[16];
    //SECRET

    if (memcmp(op(argv[1]), buf, 16) == 0) {
        printf("GG!\n");
        return 0;
    } else {
        printf("Dommage... Essaie encore!\n");
        return 1;
    }
}

BYTE * op(BYTE * str) {
    BYTE * result = malloc(16);
    for (int i = 0; i < 16; i++) {
        BYTE c = str[i];//INSTRUCTIONS
		result[i] = c;
    }
    return result;
}