#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <stdbool.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)
#define do_hypercall(hypercall_nr, arg1, arg2, arg3, arg4) asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(arg1), "c"(arg2), "d"(arg3), "e"(arg4))
#define do_hypercall(hypercall_nr, array) asm volatile(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), "b"(array[0]), "c"(array[1]), "d"(array[2]), "e"(array[3]))

#define MAX_HYPERCALL_SIZE 4


int main(int argc, char** argv)
{
    struct timespec ts_start, ts_end;
    FILE *fp;
    FILE *output;
    unsigned char filename[MAX_HYPERCALL_SIZE];
    unsigned long int buffer[MAX_HYPERCALL_SIZE];
    unsigned long int buffer_output[MAX_HYPERCALL_SIZE];
    sprintf(filename,"file.txt");

    fp = fopen("file.txt", "r");
    output = fopen("output2.txt", "w");
    if (!fp || !output){
        printf("Can not open file\n");
        return -1;
    }
    unsigned long int* arg1;
    char* arg2 = "";
    char* arg3 = "";
    char* arg4 = "";
    // printf("%lu\n",buffer);
    tic(ts_start);
    while (fgets(buffer, sizeof(buffer), fp)) {
        // do_hypercall(101,buffer[0],buffer[1],buffer[2],buffer[3]);
        buffer_output[0] = buffer[0];
        buffer_output[1] = buffer[1];
        buffer_output[2] = buffer[2];
        buffer_output[3] = buffer[3];
        fprintf(output, buffer_output);
    }
    // end
    // do_hypercall(102, filename);
    fclose(fp);
    toc(ts_end);
    return 0;
}
