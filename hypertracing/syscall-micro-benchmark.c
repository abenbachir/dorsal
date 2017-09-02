#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>
#include <sys/syscall.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

#define do_hypercall(nr, p1, p2, p3, p4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1), "c"(p2), "d"(p3), "S"(p4))

static inline int getcpu() {
    #ifdef SYS_getcpu
    int cpu, status;
    status = syscall(SYS_getcpu, &cpu, NULL, NULL);
    return (status == -1) ? status : cpu;
    #else
    return -1; // unavailable
    #endif
}
#define SAMPLES_1US 580
// keep cpu busy for 11600 -> 20us
// keep cpu busy for 5800 -> 10us
static inline void keep_cpu_busy(int microseconds){
    long int operations = 0;
    for (int j=0; j < microseconds*SAMPLES_1US; j++) {
        operations += operations * j;
    }
}

int main(int argc, char** argv)
{
    int samples = 1;
    int microseconds = 1;
    struct timespec ts_start, ts_end;

    if (argc > 1)
        microseconds = atoi(argv[1]);

    if (argc > 2)
        samples = atoi(argv[2]);

    do_hypercall(0,0,0,0,0);
    tic(ts_start);
    for (int i=0; i < samples; i++) {
        int cpu_id = getcpu(); // do syscall here
        if(microseconds > 0)
            keep_cpu_busy(microseconds);
    }
    toc(ts_end);
    long unsigned int ns = elapsed_nsec(ts_start, ts_end);
    do_hypercall(1,1,1,1,ns);
    printf("%lu\n", ns);

    FILE *fp = fopen("./results.txt", "w");
    fprintf(fp,"%lu",ns);
    fclose(fp);
    return 0;
}
