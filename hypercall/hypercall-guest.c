#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define timespec_to_nsec(timespec) (timespec.tv_nsec + 1E9 * timespec.tv_sec)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

#define do_hypercall(nr, p1, p2, p3, p4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1), "c"(p2), "d"(p3), "S"(p4))


#define do_hypercall_0() __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::)

static long long int getTimeStamp() {
    struct timeval timer_usec; 
    long long int timestamp_usec; /* timestamp in microsecond */
    if (!gettimeofday(&timer_usec, NULL)) {
        timestamp_usec = ((long long int) timer_usec.tv_sec) * 1000000000ll + 
                        (long long int) timer_usec.tv_usec;
    }
    return timestamp_usec;
}


void benchmark(int repeat)
{
    struct timespec ts_start, ts_end;
    ulong i = 0;

    for ( i=0; i < repeat; i++) {
        tic(ts_start);
        do_hypercall(i, i, i, i, i);
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        printf("%d -> %lu\n", i, ns);
        // sleep(1);
    }
}
int main(int argc, char** argv)
{
    struct timespec ts_start, ts_end;
    benchmark(10);
    /*long int i, variable, counter;
    do_hypercall(0, 0, 0, 0, 0);
    tic(ts_start);
    for(i = 0; i < 1E7; i++) {
        variable += i * variable;
        if (counter >= 1E7/10000) {
            do_hypercall(1111, i, i, i, i);
            counter = 0;
        }else{
            counter++;
        }
    }
    toc(ts_end);
    do_hypercall(1, 1, 1, 1, 1);
    unsigned long int ns = elapsed_nsec(ts_start, ts_end);
    printf("%lf\n", (double)ns/1E6);*/

/*
    unsigned long int ns1, ns2, ns3;
    tic(ts_start);
    do_hypercall_0();
    toc(ts_end);
    ns1 = elapsed_nsec(ts_start, ts_end);

    tic(ts_start);
    do_hypercall_0();
    toc(ts_end);
    ns2 = elapsed_nsec(ts_start, ts_end);

    tic(ts_start);
    do_hypercall_0();
    toc(ts_end);
    ns3 = elapsed_nsec(ts_start, ts_end);
    printf("2=%lu\n", ns1);
    printf("3=%lu\n", ns2);
    printf("4=%lu\n", ns3);

*/
    return 0;
}
