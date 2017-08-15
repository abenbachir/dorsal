#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <stdbool.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

#define do_hypercall(hypercall_nr, arg1, arg2, arg3, arg4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(arg1), "c"(arg2), "d"(arg3), "S"(arg4))

#define do_hypercall_64(nr, a0, a1, a2, a3, a4, a5, a6, a7, a8) \
    __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(a0), "c"(a1), "d"(a2), "S"(a3), \
    "r"(a4), "r"(a5), "r"(a6), "r"(a7), "r"(a8))

#define delim_hypercall(hypercall_nr, arg) asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(arg))

#define MAX_HYPERCALL_SIZE 5
#define MAX_HYPERCALL_64_SIZE 10
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

void kvm_hypercall_handler_64(unsigned long int nr,
        unsigned long int a0, unsigned long int a1, unsigned long int a2, unsigned long int a3,
        unsigned long int a4, unsigned long int a5, unsigned long int a6, unsigned long int a7, unsigned long int a8)
{
    unsigned long int buffer[MAX_HYPERCALL_64_SIZE];
    size_t size = sizeof(nr);

    memcpy(buffer, (char*)&nr, size);
    memcpy(buffer+1, (char*)&a0, size);
    memcpy(buffer+2, (char*)&a1, size);
    memcpy(buffer+3, (char*)&a2, size);
    memcpy(buffer+4, (char*)&a3, size);
    memcpy(buffer+5, (char*)&a4, size);
    memcpy(buffer+6, (char*)&a5, size);
    memcpy(buffer+7, (char*)&a6, size);
    memcpy(buffer+8, (char*)&a7, size);
    memcpy(buffer+9, (char*)&a8, size);
    // sprintf(buffer, "HYPERSTREAM: %lu %lu %lu %lu %lu", nr, a0, a1, a2, a3);
    printf("%s", buffer);
  
}

int main(int argc, char** argv)
{
    if (argc <= 1){
        printf("You must inject the filename in argment : example, ./exec file.txt\n");
        return 0;
    }

    unsigned long int nr, a0, a1, a2, a3, a4, a5, a6, a7, a8 = 0;
    struct timespec ts_start, ts_end;
    FILE *fp;
    FILE *output;
    const char* filename = argv[1];
    const char out_filename[20] = "out.txt";
    unsigned long int buffer[MAX_HYPERCALL_64_SIZE];
    unsigned long int buffer_output[MAX_HYPERCALL_64_SIZE];
        
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
    delim_hypercall(HYPERSTREAM_START_NR, hc_filename);
    tic(ts_start);
    while (fgets(buffer, sizeof(buffer), fp)) {
        // nr = buffer[0];
        // a0 = buffer[1];
        // a1 = buffer[2];
        // a2 = buffer[3];
        // a3 = buffer[4];
        // a4 = buffer[5];
        // a5 = buffer[6];
        // a6 = buffer[7];
        // a7 = buffer[8];
        // a8 = buffer[9];
        // do_hypercall_64(nr, a0, a1, a2, a3, a4, a5, a6, a7, a8);
        do_hypercall_64(buffer[0], buffer[1], buffer[2], buffer[3], buffer[4], 
            buffer[5], buffer[6], buffer[7], buffer[8], buffer[9]);

        // kvm_hypercall_handler_64(buffer[0], buffer[1], buffer[2], buffer[3], buffer[4], 
        //     buffer[5], buffer[6], buffer[7], buffer[8], buffer[9]);
        // printf("%s", buffer);
        
        // buffer_output[0] = buffer[0];
        // buffer_output[1] = buffer[1];
        // buffer_output[2] = buffer[2];
        // buffer_output[3] = buffer[3];
        // kvm_hypercall_handler(arg1, arg2, arg3, arg4, arg5);
        // puts(buffer_output);
        // fprintf(output, buffer_output);
    }
    toc(ts_end);
    printf("%lu\n", elapsed_nsec(ts_start, ts_end));
    // end
    delim_hypercall(HYPERSTREAM_END_NR, hc_filename);

    fclose(fp);
    return 0;
}
