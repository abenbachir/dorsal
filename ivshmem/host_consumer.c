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
#include "event_types.h"


int main(int argc, char **argv)
{
	const char *devicepath = "/dev/shm/chan1";
	const ssize_t device_size = 500 * 1E6; // 512MB
	struct timespec tspec;
	void *map = NULL;
	int device_fd;

	if ((device_fd = open(devicepath, O_RDWR)) < 0) {
		printf("%s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	if ((map =
	     mmap(0, device_size, PROT_READ | PROT_WRITE, MAP_SHARED, device_fd,
		  0)) == (caddr_t) - 1) {
		fprintf(stderr, "%s\n", strerror(errno));
		close(device_fd);
		exit(EXIT_FAILURE);
	}

    struct shm_config *shm_config = map;
    struct shm_event_entry *entry_map = map + sizeof(struct shm_config);

	int i = 0;
	printf("Buffer size=%lu \n", shm_config->buff_size);
	while (i < shm_config->buff_size){
		// struct shm_data_entry data_entry;
		// memcpy(&data_entry, entry_map, sizeof(data_entry));
		struct sched_switch_payload *payload = entry_map->payload;
		printf("i=%d, tsc=%llu, cpu=%d, type=%u, prev_tid=%d, "
			"next_tid=%d, prev_comm=%s, next_comm=%s \n", i, entry_map->timestamp,
			entry_map->cpu_id, entry_map->event_type, 
			payload->prev_tid, payload->next_tid, 
			payload->prev_comm, payload->next_comm);
		entry_map++;
		i++;
	}
	if ((munmap(map, device_size)) < 0)
		printf("WARNING: Failed to munmap \"%s\"\n", devicepath);

	close(device_fd);

	return 0;
}
