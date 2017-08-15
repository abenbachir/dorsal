
#include <linux/version.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/skbuff.h>
#include <linux/tracepoint.h>
#include <asm/syscall.h>
#include <linux/un.h>

#define MAX_HYPERCALL_SIZE 5
MODULE_LICENSE("GPL");

static struct tracepoint *tp_hypercall;

static void set_tracepoint(struct tracepoint *tp, void *priv) {
	printk(KERN_INFO "trace point %s\n", tp->name);
	if (strcmp(tp->name, "kvm_hypercall") == 0)
		tp_hypercall = tp;
}

void kvm_hypercall_handler(void *__data, unsigned long nr,
		unsigned long a0, unsigned long a1, unsigned long a2, unsigned long a3)
{
    unsigned long int buffer[MAX_HYPERCALL_SIZE];
    size_t size = sizeof(nr);

    memcpy(buffer, (char*)&nr, size);
    memcpy(buffer+1, (char*)&a0, size);
    memcpy(buffer+2, (char*)&a1, size);
    memcpy(buffer+3, (char*)&a2, size);
    memcpy(buffer+4, (char*)&a3, size);
    // sprintf(buffer, "HYPERSTREAM: %lu %lu %lu %lu %lu", nr, a0, a1, a2, a3);
    printk("%s", buffer);
}

//*****************************************************
// module init/exit
//*****************************************************
static int __init hyperstream_init(void) 
{
	int ret;

	for_each_kernel_tracepoint(set_tracepoint, NULL);
	if (tp_hypercall == NULL) {
		printk(KERN_INFO "hyperstream: failed to find tracepoints.\n");
		return 1;
	}
	ret = tracepoint_probe_register(tp_hypercall, kvm_hypercall_handler, NULL);

	


	printk(KERN_INFO "hyperstream: init module.\n");
	return 0;
}


static void __exit hyperstream_cleanup(void) 
{
	printk(KERN_INFO "hyperstream: removing module.\n");
	if (tp_hypercall != NULL)
		tracepoint_probe_unregister(tp_hypercall, kvm_hypercall_handler, NULL);
}


module_init(hyperstream_init);
module_exit(hyperstream_cleanup);