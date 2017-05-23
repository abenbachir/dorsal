#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

static struct timespec ts_start, ts_end;

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)
// #define do_hypercall(hypercall_nr,payload,uid, arg1, arg2, arg3) asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(payload), "c"(uid), "d"(arg1), "e"(arg2), "f"(arg3))
#define do_hypercall(hypercall_nr,payload,uid, arg1, arg2) \
    __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(payload), "c"(uid), "d"(arg1), "S"(arg2))

// static inline void do_hypercall(unsigned int hypercall_nr, int payload, unsigned long uid)
// {
//     // FIXME: should use kvm_x86_ops
//     asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(payload), "c"(uid));
// }

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


void benchmark_case1()
{
    struct timespec start, end;
    ulong i = 0;
    ulong repeat = 1E6;

    for ( i=0; i < repeat; i++) {
        tic(ts_start);
        do_hypercall(101, 0, 0, 0, 0);
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        printf("%lu,with_clock_gettime\n", ns);
    }
}

void benchmark_case2()
{
    struct timespec start, end;
    ulong samples = 1E6;
    for (int i=0; i < samples; i++) {
        // warmup
        
        int repeat = 50;
        tic(ts_start);
        for (int j=0; j < repeat; j++) {
            do_hypercall(101, 0, 0, 0, 0);
        }
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        printf("%f,no_clock_gettime\n", (double)ns/repeat);
    }
}
int main(int argc, char** argv)
{
    printf("elapsed_time\n");
    struct timespec start, end;
    ulong samples = 1E6;

    for (int i=0; i < samples; i++) {
        // warmup
        
        int repeat = 30;
        tic(ts_start);
        // for (int j=0; j < repeat; j++) {
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
            do_hypercall(0, 0, 0, 0, 0);
        // }
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        printf("%f\n", (double)ns/repeat);
    }
    return 0;
}
