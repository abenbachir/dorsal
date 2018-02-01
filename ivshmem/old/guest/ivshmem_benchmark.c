#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/time.h>
#include <time.h>

#define prfmt(fmt) "%s:%d:: " fmt, __func__, __LINE__
#define prinfo(fmt, ...) printf(prfmt(fmt), ##__VA_ARGS__)
#define prerr(fmt, ...) fprintf(stderr, prfmt(fmt), ##__VA_ARGS__)
#ifdef DEBUG
#define prdbg_p(fmt, ...) printf(fmt, ##__VA_ARGS__)
#else
#define prdbg_p(fmt, ...) do{}while(0)
#endif

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)
#define bytes_to_kb(a) (a/1E3)
#define bytes_to_mb(a) (a/1E6)

const char *devicepath = "/dev/ivshmem0";

ssize_t device_size = 512 * 1E6; // 512MB
// long lengths[] = {80, 320, 640, 1024, 4096, 8182, 16384, 32768, 65536, 1024000};
long lengths[] = {8182000,16384000,32768000};

int do_benchmark(const char* stagefile, long buffer_length)
{
    struct timespec ts_start, ts_end;
    void *map = NULL;
    int device_fd;
    FILE *fp;

    fp = fopen(stagefile, "r");
    if (!fp){
        printf("Can not open %s\n", stagefile);
        return -1;
    }

    if ((device_fd = open(devicepath, O_RDWR)) < 0) {
        prerr("%s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    if ((map =
         mmap(0, device_size, PROT_READ | PROT_WRITE, MAP_SHARED, device_fd,
          0)) == (caddr_t) - 1) {
        fprintf(stderr, "%s\n", strerror(errno));
        close(device_fd);
        exit(EXIT_FAILURE);
    }

    // start writing
    fseek(fp, 0L, SEEK_END);
    unsigned long file_size = ftell(fp);
    rewind(fp);

    // char buffer[buffer_length];
    char *buffer =  malloc(buffer_length);
    char * itr = map;
    unsigned long long read_bytes = 0;
    
    int bytes = fread(buffer, sizeof(char), buffer_length, fp);
    read_bytes += bytes;
    tic(ts_start);
    while (bytes > 0 && read_bytes < (unsigned int)device_size){

        memcpy((char *)itr, buffer, buffer_length);
        itr += buffer_length;

        // bytes = fread(buffer, sizeof(char), buffer_length, fp);
        read_bytes += bytes;
    }
    toc(ts_end);
    free(buffer);
    unsigned long stream_latency = elapsed_nsec(ts_start, ts_end);
    fclose(fp);
    long double througthput = read_bytes*8/(stream_latency/1E9);

    printf("%lu,%0.2Lf\n",
        buffer_length, (long double)througthput/1E9);
    /*printf("buffer_length=[%d B], Input [%.2f MB], transfered [%.2f MB], througthput=[%0.2Lf Gbits/s]\n",
        buffer_length,
        bytes_to_mb(file_size),
        bytes_to_mb(read_bytes), 
        (long double)througthput/1E9);*/

    if ((munmap(map, device_size)) < 0)
        prerr("WARNING: Failed to munmap \"%s\"\n", devicepath);

    close(device_fd);
}
int main(int argc, char **argv)
{
	int samples = 10;
    const char* stagefile = argv[1];
	printf("buffer size bytes, througthput Gbits/s, transfered data MB\n");
    for (int i = 0; i < sizeof(lengths)/sizeof(lengths[0]); i++ ) {
        for (int j = 0; j < samples; j++ ) {
            do_benchmark(stagefile, lengths[i]);
        }
    }
	return 0;
}
