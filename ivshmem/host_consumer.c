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


void* do_mmap(char *path, int *fd, ssize_t size)
{
	void *map;
	if ((*fd = open(path, O_RDWR)) < 0) {
		printf("%s\n", strerror(errno));
		return NULL;
	}

	if ((map =
	     mmap(0, size, PROT_READ | PROT_WRITE, MAP_SHARED, *fd,
		  0)) == (caddr_t) - 1) {
		fprintf(stderr, "%s\n", strerror(errno));
		close(fd);
		return NULL;
	}
	return map;
}

void do_munmap(void *map, int *fd, char *path, ssize_t size)
{
	if ((munmap(map, size)) < 0)
		printf("WARNING: Failed to munmap \"%s\"\n", path);

	close(*fd);
}

int main(int argc, char **argv)
{
	char *vmsyncpath = "/proc/host_vmsync1";
	ssize_t vmsync_size = 4096; // 1 page
	char *devicepath = "/dev/shm/chan1";
	ssize_t device_size = 500 * 1E6; // 512MB
	struct timespec tspec;
	void *map = NULL;
	void *vmsync_map = NULL;
	int device_fd, vmsync_fd;
	

	vmsync_map = do_mmap(vmsyncpath, &vmsync_fd, vmsync_size);
	map = do_mmap(devicepath, &device_fd, device_size);

	printf("map=%lu \n", (unsigned long*)map);
    struct shm_config *shm_config = map;
    struct shm_event_entry *entry_map = map + sizeof(struct shm_config);

	
	// struct mmap_info *mmap_info = map;
	// printf("data=%s \n", mmap_info->data);

	// mmap_info->data[0] = 'a';

	// printf("data=%s \n", mmap_info->data);


	// strcmp(mmap_info->data, "asdf");
    
    if(!vmsync_map)
    	goto end;
    unsigned long long i = 0;
    while (1) {
    	struct host_vmsync *vmsync = vmsync_map;
    	if(vmsync->spinlock <= 0) {
    		// printf("spinlock =%d\n", vmsync->spinlock); 
    		// sleep(0.001);
    		continue;
    	}
    	// printf("spinlock =%d\n", vmsync->spinlock); 
    	struct shm_event_entry *kvm_exit = &vmsync->kvm_exit;
    	struct kvm_exit_payload *payload = kvm_exit->payload;
		printf("vmsync entry: exit=%u, tsc=%llu, cpu=%d, type=%u isa=%u guest_rip=%lu\n", 
			payload->exit_reason,
			kvm_exit->timestamp, 
			kvm_exit->cpu_id, 
			kvm_exit->event_type,
			payload->isa,
			payload->guest_rip);

		vmsync->spinlock = 0;
		// if(i++ >= 100000)
		// 	break;
    }
	
	
	// int i = 0;
	// while (i < shm_config->buff_size){
	// 	// struct shm_data_entry data_entry;
	// 	// memcpy(&data_entry, entry_map, sizeof(data_entry));
	// 	struct sched_switch_payload *payload = entry_map->payload;
	// 	printf("i=%d, tsc=%llu, cpu=%d, type=%u, prev_tid=%d, "
	// 		"next_tid=%d, prev_comm=%s, next_comm=%s \n", i, entry_map->timestamp,
	// 		entry_map->cpu_id, entry_map->event_type, 
	// 		payload->prev_tid, payload->next_tid, 
	// 		payload->prev_comm, payload->next_comm);
	// 	entry_map++;
	// 	i++;
	// }
	
end:
	do_munmap(map, devicepath, &device_fd, device_size);
	do_munmap(vmsync_map, vmsyncpath, &vmsync_fd, vmsync_size);
	return 0;
}
