#define BYTE unsigned char

void operation(BYTE* buf) {
    for (int i = 0; i < 16; i++) {
        BYTE c = buf[i];//INSTRUCTIONS
        buf[i] = c;
    }
}

int main(int argc, BYTE* argv[]) {
    return 0;
}