#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <qemu-hypertrace.h>

static struct timespec ts_start, ts_end;

static inline void tic(){
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts_start);
}

static inline uint64_t toc(){
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts_end);
    return (ts_end.tv_nsec + 1E9 * ts_end.tv_sec) - (ts_start.tv_nsec + 1E9 * ts_start.tv_sec);
}

int main(int argc, char **argv)
{
    char *base = NULL;
    if (argc > 1) {
        base = argv[1];
    }
    /* In 'user' mode this path must be the same we will use to start QEMU. */
    if (qemu_hypertrace_init(base) != 0) {
        perror("error: qemu_hypertrace_init");
        abort();
    }
    /* Set additional event arguments */
    uint64_t client  = 0;
    uint64_t *data = qemu_hypertrace_data(client);
    uint64_t *control_addr = qemu_hypertrace_control();
    ulong i = 0;
    ulong repeat = 1E6;
    printf("-------- Start benchmark --------- \n");   
    tic();
    for ( i=0; i < repeat; i++) {
        // qemu_hypertrace(client, i);
        // do_hypertrace(client, i);
        control_addr[client] = i;
    }
    uint64_t ns = toc();
    printf("elapsed : %ld ns \n", ns);
    printf("event cost : %f ns \n", (double)ns/repeat);
    // printf("event freq : %f ns \n", (double)1000 * 1 / (ns / repeat));
    return 0;
}

