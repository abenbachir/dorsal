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
#define timespec_to_nsec(tspec) (tspec.tv_nsec + 1E9 * tspec.tv_sec)
#define bytes_to_kb(a) (a/1E3)
#define bytes_to_mb(a) (a/1E6)

struct shm_config_chan {
    // int can_write;
    unsigned long counter;
};

struct shm_data_chan {
    unsigned long entires;
};

struct shm_data_entry {
    unsigned long long timestamp;
    unsigned int event_type;
    unsigned int cpu_id;
    int data;
    char payload[80];
};

int main(int argc, char **argv)
{
	const char *devicepath = "/dev/ivshmem0";
	const ssize_t device_size = 500 * 1E6; // 512MB
	struct timespec tspec;
	void *map = NULL;
	int device_fd;

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

    struct shm_config_chan *config_map = map;
    struct shm_data_entry *entry_map = map + sizeof(struct shm_config_chan);

    
	config_map->counter = 0;
	while (config_map->counter < 11) {
		tic(tspec);
		struct shm_data_entry data_entry = {
			.timestamp = timespec_to_nsec(tspec),
			.data = config_map->counter,
			.cpu = 0,
		};

		memcpy(entry_map, &data_entry, sizeof(data_entry));
		entry_map++;

		config_map->counter++;
	}

    entry_map = map + sizeof(struct shm_config_chan);

	int i = 0;
	printf("Counter=%lu \n", config_map->counter);
	while (i < config_map->counter){
		// struct shm_data_entry data_entry;
		// memcpy(&data_entry, entry_map, sizeof(data_entry));
		printf("i=%d, timestamp=%llu, data=%d \n", i, entry_map->timestamp, entry_map->data);
		entry_map++;
		i++;
	}
	if ((munmap(map, device_size)) < 0)
		prerr("WARNING: Failed to munmap \"%s\"\n", devicepath);

	close(device_fd);

	return 0;
}
