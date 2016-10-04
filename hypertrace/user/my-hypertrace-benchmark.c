#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <qemu-hypertrace.h>

// I made this external global variable to run my micro benchmarks
__thread uint64_t *control_addr;
// #define do_hypertrace(client, arg1) control_addr[client] = arg1

int timeval_subtract(struct timeval *result, struct timeval *t2, struct timeval *t1)
{
    long int diff = (t2->tv_usec + 1000000 * t2->tv_sec) - (t1->tv_usec + 1000000 * t1->tv_sec);
    result->tv_sec = diff / 1000000;
    result->tv_usec = diff % 1000000;

    return (diff<0);
}


int main(int argc, char **argv)
{
    struct timeval tvBegin, tvEnd, tvDiff;
    char *base = NULL;
    if (argc > 1) {
        base = argv[1];
    }

    /* In 'user' mode this path must be the same we will use to start QEMU. */
    if (qemu_hypertrace_init(base) != 0) {
        perror("error: qemu_hypertrace_init");
        abort();
    }


    printf("Start benchmark \n");

    /* Set additional event arguments */
    uint64_t client  = 0;
    uint64_t *data = qemu_hypertrace_data(client);
    // begin
    ulong i = 0;
    ulong repeat = 1E6;
    gettimeofday(&tvBegin, NULL);
    for ( i=0; i < repeat; i++) {
        // do_hypertrace(client, i);
        control_addr[client] = i;
    }
    //end
    gettimeofday(&tvEnd, NULL);
    timeval_subtract(&tvDiff, &tvEnd, &tvBegin);

    uint64_t ns = tvDiff.tv_sec*(uint64_t)1E9 + tvDiff.tv_usec*1E3;
    printf("elapsed : %ld ns \n", ns);
    printf("event cost : %f ns \n", (double)ns/repeat);
    printf("event freq : %f ns \n", (double)1000 * 1 / (ns / repeat));
    return 0;
}

