#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

static struct timespec ts_start, ts_end;

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

#define do_hypercall_0() __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::)
#define do_hypercall_1(nr) __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr))
#define do_hypercall_2(nr, p1) __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1))
#define do_hypercall_3(nr, p1, p2) __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1), "c"(p2))
#define do_hypercall_4(nr, p1, p2, p3) __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1), "c"(p2), "d"(p3))
#define do_hypercall_5(nr, p1, p2, p3, p4) __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1), "c"(p2), "d"(p3), "S"(p4))

void nsleep(long nanoseconds)
{
    const int call_cost = 50; // nanosecond cost by default
    if(nanoseconds <= call_cost)
        return;
    long int diff = 0;
    struct timespec t_start, t_end;
    unsigned long int time_elapsed = 0;
    tic(t_start);
    do{
        toc(t_end);
        time_elapsed = elapsed_nsec(t_start, t_end) + call_cost;
        diff = nanoseconds - time_elapsed;
        // printf("difference %d\n", diff);
    }while(diff >= 0);
}


void benchmark_case1(int repeat/* 1E6 */)
{
    struct timespec start, end;
    ulong i = 0;

    for ( i=0; i < repeat; i++) {
        tic(ts_start);
        do_hypercall_5(i,i,i,i,i);
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        printf("%lu,with_clock_gettime\n", ns);
    }
}

void benchmark_case2(int repeat/* 50 */)
{
    struct timespec start, end;
    ulong samples = 1E6;
    for (int i=0; i < samples; i++) {
        // warmup
        
        tic(ts_start);
        for (int j=0; j < repeat; j++) {
            do_hypercall_5(j,j,j,j,j);
        }
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        printf("%f,no_clock_gettime\n", (double)ns/repeat);
    }
}
int main(int argc, char** argv)
{
    printf("elapsed_time\n");
    struct timespec ts_start, ts_end;
    ulong samples = 1E5;

    for (int i=0; i < samples; i++) {
        int repeat = 30;
        tic(ts_start);
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
            do_hypercall_0();
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        printf("%f\n", (double)ns/repeat);
    }
    return 0;
}
