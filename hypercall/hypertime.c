#include <stdio.h>
#include <stdlib.h>


#define do_hypercall(nr, p1, p2, p3, p4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1), "c"(p2), "d"(p3), "S"(p4))


int main(int argc, char** argv)
{
    if(argc <= 1)
        do_hypercall(0, 0, 0, 0, 0);
    else
        do_hypercall(1, 1, 1, 1, 1);
    return 0;
}
