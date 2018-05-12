#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>
#include <pthread.h>
#include <sched.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

#define do_hypercall(nr, p1, p2, p3, p4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1), "c"(p2), "d"(p3), "S"(p4))


pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

// keep cpu busy for 11600 -> 20us
// keep cpu busy for 5800 -> 10us
static inline void keep_cpu_busy(float microseconds)
{
    const int factor_1us = 580;
    long int operations = 0;
    for (int j=0; j < microseconds*factor_1us; j++) {
        operations += operations * j;
    }
}

void *do_work(void *args)
{
    unsigned int tid = (unsigned int)pthread_self();
    int pid = getpid();
    int samples = (int) args;

//    printf("pid=%d, tid=%u, samples=%d\n", pid, tid, samples);
    for (int i = 0; i < samples; i++)
    {
        pthread_mutex_lock(&mutex);
        keep_cpu_busy(0.01);
        sched_yield();
        pthread_mutex_unlock(&mutex);
        sched_yield();
    }
}

int main(int argc, char** argv)
{
    int i, j;
    int number_threads = 2;
    int samples = 10;
    struct timespec ts_start, ts_end;

    if (argc > 1)
        number_threads = atoi(argv[1]);

    if (argc > 2)
        samples = atoi(argv[2]);
    tic(ts_start);

    pthread_t thread_id[number_threads];

    do_hypercall(0,0,0,0,0);
    for (i=0; i < number_threads; i++)
        pthread_create(&thread_id[i], NULL, do_work, (void *)samples);

    for (j=0; j < number_threads; j++)
        pthread_join(thread_id[j], NULL);

    do_hypercall(1,1,1,1,1);
    toc(ts_end);
    long unsigned int ns = elapsed_nsec(ts_start, ts_end);
    printf("%d,%lu,\n", samples, ns);

    return 0;
}
