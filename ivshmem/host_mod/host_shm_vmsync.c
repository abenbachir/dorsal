/*
 *
 * Host_shm_vmsync : Write sync
 *
 * Copyright (c) 2018-2017 Abderrahmane Benbachir <abderrahmane.benbachir@polymtl.ca>
 *
 */
#include <linux/version.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/skbuff.h>
#include <linux/tracepoint.h>
#include <linux/kvm_host.h>
#include <linux/un.h>
#include <linux/proc_fs.h>
#include "../mod.h"
#include "../event_types.h"
#define PROC_ENTRY_NAME "host_shm_vmsync"

static const struct file_operations mod_operations = {
	.write = mod_write,
	.read = mod_read
};

static void kvm_exit_handler(void *__data, unsigned int exit_reason,
	struct kvm_vcpu *vcpu, u32 isa)
{
	if(!is_tracing_enabled())
		return;
	// int cpu = smp_processor_id();
	printk("kvm_exit exit_reason=%u\n", exit_reason);
}

static void kvm_entry_handler(void *__data, unsigned int vcpu_id)
{	
	if(!is_tracing_enabled())
		return;
	// int cpu = smp_processor_id();
	printk("kvm_entry vcpu_id=%u\n", vcpu_id);
}

static struct tracepoint_entry tracepoint_table[] = {
	{ .name = "kvm_entry", 		.probe = kvm_entry_handler },
	{ .name = "kvm_exit", 		.probe = kvm_exit_handler },
};

struct tracepoint_entries tp_entries = {
	.size = ARRAY_SIZE(tracepoint_table),
	.entries = tracepoint_table,
};

static int mod_tracepoint_notify(struct notifier_block *self,
		unsigned long val, void *data)
{
	struct tp_module *tp_mod = data;
	int ret = 0;

	switch (val) {
		case MODULE_STATE_COMING:
			
			ret = mod_tracepoint_coming(tp_mod, set_tracepoint, &tp_entries);
			break;
		case MODULE_STATE_GOING:
			// ...
			break;
		default:
			break;
	}
	return ret;
}

static struct notifier_block mod_tracepoint_notifier = {
	.notifier_call = mod_tracepoint_notify,
	.priority = 0,
};
/*
 * module init/exit
 */
static int __init host_shm_vmsync_init(void)
{
	int ret;

	ret = register_tracepoint_module_notifier(&mod_tracepoint_notifier);
	if(ret)
		return ret;

	proc_create_data(PROC_ENTRY_NAME, S_IRUGO | S_IWUGO, NULL,
            &mod_operations, NULL);

	printk(KERN_INFO "host_shm_vmsync: init module.\n");
	return 0;
}

static void __exit host_shm_vmsync_cleanup(void)
{
	remove_proc_entry(PROC_ENTRY_NAME, NULL);

	unregister_all_probes(&tp_entries);

	// synchronize_rcu();
	unregister_tracepoint_module_notifier(&mod_tracepoint_notifier);

	printk(KERN_INFO "host_shm_vmsync: removing module.\n");
}

module_init(host_shm_vmsync_init);
module_exit(host_shm_vmsync_cleanup);

MODULE_LICENSE("GPL and additional rights");
MODULE_AUTHOR("Abderrahmane Benbachir <abderrahmane.benbachir@polymtl.ca>");
MODULE_DESCRIPTION("Host_shm_vmsync");
MODULE_VERSION("1.0");