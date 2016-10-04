#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>


#define do_hypercall(hypercall_nr,payload,uid) asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(payload), "c"(uid))

/**
 * timeval_to_ns - Convert timeval to nanoseconds
 * @ts:     pointer to the timeval variable to be converted
 *
 * Returns the scalar nanosecond representation of the timeval
 * parameter.
 *
 * Ripped from linux/time.h because it's a kernel header, and thus
 * unusable from here.
 */
static inline long long timeval_to_ns(const struct timeval *tv)
{
    return ((long long) tv->tv_sec * 1E9) +
        tv->tv_usec * 1000;
}

static inline int timeval_subtract(struct timeval *result, struct timeval *t2, struct timeval *t1)
{
    long int diff = (t2->tv_usec + 1000000 * t2->tv_sec) - (t1->tv_usec + 1000000 * t1->tv_sec);
    result->tv_sec = diff / 1000000;
    result->tv_usec = diff % 1000000;

    return (diff<0);
}

// static inline void do_hypercall(unsigned int hypercall_nr, int payload, unsigned long uid)
// {
//     // FIXME: should use kvm_x86_ops
//     asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(payload), "c"(uid));
// }
int main(int argc, char** argv)
{
    struct timeval tvBegin, tvEnd, tvDiff;

    printf("Simple hypercall \n");
    ulong i = 0;
    ulong repeat = 1E7;

    gettimeofday(&tvBegin, NULL);
    for ( i=0; i < repeat; i++) {
        do_hypercall(0, 0, i);
    }
    gettimeofday(&tvEnd, NULL);

    timeval_subtract(&tvDiff, &tvEnd, &tvBegin);
    unsigned long int ns = timeval_to_ns(&tvDiff);
    printf("elapsed : %lu ns \n", ns);
    printf("event cost : %f ns \n", (double)ns/repeat);
    printf("event freq : %f ns \n", (double)1000 * 1 / (ns / repeat));
    return 0;
}
