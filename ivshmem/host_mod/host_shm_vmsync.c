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
#include <linux/kvm_host.h>
#include <../arch/x86/kvm/kvm_cache_regs.h>

#include "../mod.h"
#include "../event_types.h"
#define PROC_ENTRY_NAME "host_shm_vmsync"
#define PROC_VMSYNC_NAME "host_vmsync1"
// #define BUFFER_SIZE 4096
#define BUFFER_SIZE 500 * 1E6

struct mmap_info {
	char *data;
};

struct mmap_info *mmap_info;

static const struct file_operations mod_operations = {
	.write = mod_write,
	.read = mod_read
};

static void kvm_exit_handler(void *__data, unsigned int exit_reason,
	struct kvm_vcpu *vcpu, u32 isa)
{
	if(!is_tracing_enabled())
		return;
	struct host_vmsync *vmsync = (struct host_vmsync*)mmap_info->data;
	struct shm_event_entry *event_entry = &vmsync->kvm_exit;

	printk("kvm_exit exit_reason=%u spinlock=%llu\n", exit_reason, vmsync->spinlock);
	event_entry->cpu_id = smp_processor_id();
	event_entry->event_type = KVM_EXIT_EVENT_NR;
	struct kvm_exit_payload *payload = (struct kvm_exit_payload *)event_entry->payload;
	payload->isa = isa;
	payload->guest_rip = kvm_rip_read(vcpu);
	payload->exit_reason = exit_reason;
	event_entry->timestamp = local_clock();
	vmsync->spinlock++;
}

static void kvm_entry_handler(void *__data, unsigned int vcpu_id)
{	
	if(!is_tracing_enabled())
		return;
	// printk("kvm_entry vcpu_id=%u\n", vcpu_id);
}

static struct tracepoint_entry tracepoint_table[] = {
	// { .name = "kvm_entry", 		.probe = kvm_entry_handler },
	// { .name = "kvm_exit", 		.probe = kvm_exit_handler },
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

/* First page access. */
static int vm_fault(struct vm_fault *vmf)
{
	struct vm_area_struct *vma = vmf->vma;
	struct page *page;
	struct mmap_info *info;

	info = (struct mmap_info *)vma->vm_private_data;
	if (info->data) {
		page = virt_to_page(info->data);
		get_page(page);
		vmf->page = page;
	}
	return 0;
}

static struct vm_operations_struct vm_ops =
{
	.fault = vm_fault,
};

static int mmap(struct file *filp, struct vm_area_struct *vma)
{
	vma->vm_ops = &vm_ops;
	vma->vm_flags |= VM_DONTEXPAND | VM_DONTDUMP;
	vma->vm_private_data = filp->private_data;
	return 0;
}

static int open(struct inode *inode, struct file *filp)
{
	filp->private_data = mmap_info;
	return 0;
}

static int release(struct inode *inode, struct file *filp)
{
	filp->private_data = NULL;
	return 0;
}

static const struct file_operations vmsync_ops = {
	.mmap = mmap,
	.open = open,
	.release = release,
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

	mmap_info = kmalloc(sizeof(struct mmap_info), GFP_KERNEL);
	mmap_info->data = (char *)get_zeroed_page(GFP_KERNEL);
	struct host_vmsync *vmsync = (struct host_vmsync*)mmap_info->data;
	vmsync->spinlock = 0;
	proc_create(PROC_VMSYNC_NAME, 0, NULL, &vmsync_ops);

	printk(KERN_INFO "host_shm_vmsync: init module.\n");
	return 0;
}

static void __exit host_shm_vmsync_cleanup(void)
{
	free_page((unsigned long)mmap_info->data);
	kfree(mmap_info);
	remove_proc_entry(PROC_VMSYNC_NAME, NULL);

	remove_proc_entry(PROC_ENTRY_NAME, NULL);

	unregister_all_probes(&tp_entries);

	synchronize_rcu();
	unregister_tracepoint_module_notifier(&mod_tracepoint_notifier);

	printk(KERN_INFO "host_shm_vmsync: removing module.\n");
}

module_init(host_shm_vmsync_init);
module_exit(host_shm_vmsync_cleanup);

MODULE_LICENSE("GPL and additional rights");
MODULE_AUTHOR("Abderrahmane Benbachir <abderrahmane.benbachir@polymtl.ca>");
MODULE_DESCRIPTION("Host_shm_vmsync");
MODULE_VERSION("1.0");