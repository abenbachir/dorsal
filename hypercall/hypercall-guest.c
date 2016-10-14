#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

static struct timespec ts_start, ts_end;

#define tic() clock_gettime(CLOCK_MONOTONIC, &ts_start)
#define toc() clock_gettime(CLOCK_MONOTONIC, &ts_end)
#define elapsed_nsec() (ts_end.tv_nsec + 1E9 * ts_end.tv_sec) - (ts_start.tv_nsec + 1E9 * ts_start.tv_sec)
#define do_hypercall(hypercall_nr,payload,uid) asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(payload), "c"(uid))


int main(int argc, char** argv)
{
    struct timeval tvBegin, tvEnd, tvDiff;

    printf("Simple hypercall \n");
    tic();
    do_hypercall(101, 2016, 1);
    toc();
    unsigned long int ns = elapsed_nsec();
    printf("event cost : %f ns \n", (double)ns/6);
    return 0;
}
