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

int main(int argc, char **argv)
{
	const char *devicepath = "/dev/ivshmem0";
    const char* stagefile = argv[1];
	struct timespec ts_start, ts_end;
	ssize_t device_size = 512 * 1000;
	void *map = NULL;
	int device_fd;
    FILE *fp;

	fp = fopen(stagefile, "r");
    if (!fp){
        printf("Can not open %s %d\n", stagefile, fp);
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
    const int buffer_size = 1 << 10;
    char buffer[buffer_size];
    tic(ts_start);
    while (fgets(buffer, sizeof(buffer), fp)) {
    	strcpy((char *)map, buffer);
    }
    toc(ts_end);
    unsigned long stream_latency = elapsed_nsec(ts_start, ts_end);

    long double througthput = file_size*8/(stream_latency/1E9);
    printf("Practical througthput=%Lf Gbits/s\n", (long double)througthput/1E9);

	if ((munmap(map, device_size)) < 0)
		prerr("WARNING: Failed to munmap \"%s\"\n", devicepath);

	close(device_fd);

	return 0;
}
