#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <stdbool.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

#define do_hypercall(hypercall_nr, arg1, arg2, arg3, arg4) __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(arg1), "c"(arg2), "d"(arg3), "S"(arg4))
#define delim_hypercall(hypercall_nr, arg) asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(arg))

#define MAX_HYPERCALL_SIZE 5
#define HYPERSTREAM_START_NR 900
#define HYPERSTREAM_NR 901
#define HYPERSTREAM_END_NR 902

void kvm_hypercall_handler(unsigned long int nr,
        unsigned long int a0, unsigned long int a1, unsigned long int a2, unsigned long int a3)
{
    unsigned long int buffer[MAX_HYPERCALL_SIZE];
    size_t size = sizeof(nr);

    memcpy(buffer, (char*)&nr, size);
    memcpy(buffer+1, (char*)&a0, size);
    memcpy(buffer+2, (char*)&a1, size);
    memcpy(buffer+3, (char*)&a2, size);
    memcpy(buffer+4, (char*)&a3, size);
    // sprintf(buffer, "HYPERSTREAM: %lu %lu %lu %lu %lu", nr, a0, a1, a2, a3);
    printf("%s", buffer);
  
}

int main(int argc, char** argv)
{
    if (argc <= 1){
        printf("You must inject the filename in argment : example, ./exec file.txt\n");
        return 0;
    }

    unsigned long int arg1, arg2, arg3, arg4, arg5 = 0;
    struct timespec ts_start, ts_end;
    FILE *fp;
    FILE *output;
    const char* filename = argv[1];
    const char out_filename[20] = "out.txt";
    unsigned long int buffer[MAX_HYPERCALL_SIZE];
    unsigned long int buffer_output[MAX_HYPERCALL_SIZE];
        
    fp = fopen(filename, "r");
    if (!fp){
        printf("Can not open %s %d\n", filename, fp);
        return -1;
    }
    // output = fopen(out_filename, "w");
    // if (!output){
    //     printf("Can not open %s\n",out_filename);
    //     return -1;
    // }
    
    unsigned long int hc_filename = 0;
    memcpy(&hc_filename, filename, sizeof(hc_filename));
    tic(ts_start);
    delim_hypercall(HYPERSTREAM_START_NR, hc_filename);
    while (fgets(buffer, sizeof(buffer), fp)) {
        // do_hypercall(HYPERTREAM_NR,buffer[0],buffer[1],buffer[2],buffer[3]);
        arg1 = buffer[0];
        arg2 = buffer[1];
        arg3 = buffer[2];
        arg4 = buffer[3];
        arg5 = buffer[4];
        // memcpy(&arg1, buffer, sizeof(arg1));
        // memcpy(&arg2, buffer+1, sizeof(arg2));
        // memcpy(&arg3, buffer+2, sizeof(arg3));
        // memcpy(&arg4, buffer+3, sizeof(arg4));
        do_hypercall(arg1, arg2, arg3, arg4, arg5);
        // printf("%s", buffer);
        
        // buffer_output[0] = buffer[0];
        // buffer_output[1] = buffer[1];
        // buffer_output[2] = buffer[2];
        // buffer_output[3] = buffer[3];
        // kvm_hypercall_handler(arg1, arg2, arg3, arg4, arg5);
        // puts(buffer_output);
        // fprintf(output, buffer_output);
    }
    // end
    delim_hypercall(HYPERSTREAM_END_NR, hc_filename);
    toc(ts_end);
    unsigned long int nanoseconds = elapsed_nsec(ts_start, ts_end);

    fclose(fp);

    printf("%lu\n", nanoseconds);
    return 0;
}
