#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <stdbool.h>


static struct timespec ts_start, ts_end;

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)
#define do_hypercall(hypercall_nr,payload,uid, arg1, arg2) asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(payload), "c"(uid), "d"(arg1), "e"(arg2))


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

unsigned int hypercount(unsigned int nanoseconds)
{
    long int diff = 0, count = 0, time_elapsed = 0;
    struct timespec t_start, t_end;
    tic(t_start);
    do{
        do_hypercall(101, 0xca, 0xce, 0xfa, 0x100);
        count++;
        toc(t_end);
        time_elapsed = elapsed_nsec(t_start, t_end);
        diff = nanoseconds - time_elapsed;
        // printf("difference %d\n", diff);
    }while(diff >= 0);

    return count;
}

void cpu_burn(unsigned int n)
{
    double x;
    while (n-- > 0) {
        x = sin(log(x+10)) + 1.1;
        x = sqrt(x*3.9 + x*x/4.2); 
        // printf("%f\n",x);
    }
}
int main(int argc, char** argv)
{
    
    //printf("----------- Hypercount benchmark ----------\n");
    printf("duration,hypercalls\n");
    unsigned long int ns_max_duration = 1E6; 
    unsigned long int ns_increment = 300; 
    unsigned long int period = ns_increment;
    for(; period < ns_max_duration; period+=ns_increment)
    {
        unsigned long int count = hypercount(period);
        // hypercount(period);
        printf("%lu,%lu\n", period, count);
        // cpu_burn(1E5);
    }
    
    // printf("elapsed : %lu ns\n", nanoseconds);
    // printf("Number hypercalls been made : %lu \n", count);
    // printf("event freq : %f ns \n", (double)1000 * 1 / (ns / repeat));
    return 0;
}
