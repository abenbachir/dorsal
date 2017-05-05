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

int main(int argc, char** argv)
{
    struct timespec start, end;
    printf("----------- Hypercall benchmark ----------\n");
    printf("Cost\n");
    ulong i = 0;
    ulong repeat = 1E6;
    // tic(start);
    for ( i=0; i < repeat; i++) {
        tic(ts_start);
        do_hypercall(101, 0, 0, 0, 0); // ts_start.tv_nsec + 1E9 * ts_start.tv_sec
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        printf("%lu\n", ns);
        // nsleep(1000000);
    }
    // toc(end);
    // unsigned long int ns = elapsed_nsec(start, end);

    // printf("elapsed : %lu ns \n", ns);
    // printf("event cost : %f ns \n", (double)ns/repeat);
    // printf("event freq : %f ns \n", (double)1000 * 1 / (ns / repeat));
    return 0;
}
