/*
 *
 * Guest_shm_trace : tracer specific for virtual machine.
 *
 * Copyright (c) 2018-2017 Abderrahmane Benbachir <abderrahmane.benbachir@polymtl.ca>
 * Copyright (c) 2018-2017 Hani Nemati <hani.nemati@polymtl.ca>
 *
 */
#include <linux/version.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/skbuff.h>
#include <linux/tracepoint.h>
#include <asm/syscall.h>
#include <linux/un.h>
#include <linux/proc_fs.h>
#include <linux/trace_clock.h>
#include "../mod.h"
#include "../event_types.h"
#include "guest_pci_device.h"

#define PROC_ENTRY_NAME "guest_shm_trace"

static struct shm_config* shm_config;
static struct shm_event_entry* current_entry;
static struct ivshmem_dev_t* ivshmem_dev;

static const struct file_operations mod_operations = {
	.write = mod_write,
    .read = mod_read
};

void setup_shm_regions(struct ivshmem_dev_t* shmem_dev) {
	shm_config = shmem_dev->data_base_addr;
	// reset
	shm_config->buff_size = 0;

	current_entry = shmem_dev->data_base_addr + sizeof(struct shm_config);
	if(shm_config->buff_size)
		current_entry += shm_config->buff_size;

}
static void probe_sched_switch(void *ignore, bool preempt,
           struct task_struct *prev, struct task_struct *next)
{
	// long int* buf = (long int*)next->comm;
	struct shm_event_entry* entry;
	if(!is_tracing_enabled())
		return;

	entry = current_entry++;
	shm_config->buff_size++;

	entry->timestamp = local_clock();
	entry->cpu_id = smp_processor_id();
	entry->event_type = SCHED_SWITCH_EVENT_NR;
	printk("i=%d) sched_switch tsc=%llu cpu_id=%u type=%u", 
		shm_config->buff_size-1, 
		entry->timestamp, entry->cpu_id, entry->event_type
	);
	struct sched_switch_payload payload = {
		.prev_tid = prev->pid,
		.next_tid = next->pid,
		.prev_prio = prev->prio - MAX_RT_PRIO,
		.next_prio = next->prio - MAX_RT_PRIO,
		.prev_state = prev->state,
	};
	strcpy(payload.prev_comm, prev->comm);
	strcpy(payload.next_comm, next->comm);
	memcpy(&entry->payload, &payload, sizeof(payload));
}
//*****************************************************
// Syscall filtering
//*****************************************************
void probe_sys_enter(void *__data, struct pt_regs *regs, long id)
{ 
	if(!is_tracing_enabled())
		return;
    // do_hypercall(GUEST_SHM_TRACE_SYS_ENTER_NR, id, 0, 0, 0);
}

void probe_sys_exit(void *__data, struct pt_regs *regs, long ret)
{
	long id;
	long ret_val;

	if(!is_tracing_enabled())
		return;
	// printk(KERN_INFO "hypertracing %u: syscall exit ret=%d\n", current->pid, ret);
	id = syscall_get_nr(current, regs);

	ret_val = syscall_get_return_value(current, regs);

    // do_hypercall(GUEST_SHM_TRACE_SYS_EXIT_NR, id, ret_val, 0, 0);

}

static struct tracepoint_entry tracepoint_table[] = {
	{ .name = "sched_switch", 	.probe = probe_sched_switch },
	{ .name = "sys_enter", 		.probe = probe_sys_enter },
	{ .name = "sys_exit", 		.probe = probe_sys_exit },
};
struct tracepoint_entries tp_entries = {
	.size = ARRAY_SIZE(tracepoint_table),
	.entries = tracepoint_table,
};


static int __init guest_shm_trace_init(void) 
{
	ivshmem_dev = get_ivshmem_dev();
	setup_shm_regions(ivshmem_dev);

	for_each_kernel_tracepoint(set_tracepoint, &tp_entries);

	proc_create_data(PROC_ENTRY_NAME, S_IRUGO | S_IWUGO, NULL,
            &mod_operations, NULL);

	printk(KERN_INFO "guest_shm_trace: init module.\n");
	return 0;
}


static void __exit guest_shm_trace_cleanup(void) {
	printk(KERN_INFO "guest_shm_trace: removing module.\n");

	unregister_all_probes(&tp_entries);

	remove_proc_entry(PROC_ENTRY_NAME, NULL);
}

module_init(guest_shm_trace_init);
module_exit(guest_shm_trace_cleanup);

MODULE_LICENSE("GPL and additional rights");
MODULE_AUTHOR("Abderrahmane Benbachir <abderrahmane.benbachir@polymtl.ca>");
MODULE_DESCRIPTION("Guest_shm_trace");
MODULE_VERSION("1.0");