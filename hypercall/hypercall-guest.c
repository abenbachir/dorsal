#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

#define do_hypercall(nr, p1, p2, p3, p4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1), "c"(p2), "d"(p3), "S"(p4))



void benchmark(int repeat)
{
    struct timespec ts_start, ts_end;
    ulong i = 0;

    for ( i=0; i < repeat; i++) {
        tic(ts_start);
        do_hypercall(i, i, i, i, i);
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        printf("%lu\n", ns);
        // sleep(1);
    }
}
int main(int argc, char** argv)
{
    benchmark(3);
    return 0;
}
