
#include <linux/version.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/skbuff.h>
#include <linux/tracepoint.h>
#include <asm/syscall.h>
#include <linux/un.h>

#define do_hypercall(nr, p1, p2, p3, p4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), \
    "b"(p1), \
    "c"(p2), \
    "d"(p3), \
    "S"(p4))

MODULE_LICENSE("GPL");

static struct tracepoint *tp_sysenter;
static struct tracepoint *tp_sysexit;

static void set_tracepoint(struct tracepoint *tp, void *priv) {
	//printk(KERN_INFO "trace point %s\n", tp->name);
	if (strcmp(tp->name, "sys_enter") == 0)
		tp_sysenter = tp;

	if (strcmp(tp->name, "sys_exit") == 0)
		tp_sysexit = tp;
}

//*****************************************************
// Syscall filtering
//*****************************************************
void syscall_entry_probe(void *__data, struct pt_regs *regs, long id)
{
    if (id == 309){
        do_hypercall(4000, id, 0, 0, 0);
    }
}

void syscall_exit_probe(void *__data, struct pt_regs *regs, long ret)
{
	long id;

	// printk(KERN_INFO "hypertracing %u: syscall exit ret=%d\n", current->pid, ret);
	id = syscall_get_nr(current, regs);

    if (id == 309){
        do_hypercall(4000, id, 1, ret, 0);
    }

}
//*****************************************************
// module init/exit
//*****************************************************

//extern struct nsproxy init_nsproxy;
static int __init syscall_hypertracing_init(void) {
	int ret;

	for_each_kernel_tracepoint(set_tracepoint, NULL);
	 if (tp_sysenter == NULL) {
	 	printk(KERN_INFO "syscall_hypertracing: failed to find sys_enter tracepoints.\n");
	 	return 1;
	 }
	 ret = tracepoint_probe_register(tp_sysenter, syscall_entry_probe, NULL);

	 if (ret) {
	 	printk(KERN_INFO "syscall_hypertracing: failed initializing syscall_entry_probe.\n");
	 	return 1;
	 }

	 if (tp_sysexit == NULL) {
	 	printk(KERN_INFO "syscall_hypertracing: failed to find sys_exit tracepoints.\n");
	 	return 1;
	 }
	 ret = tracepoint_probe_register(tp_sysexit, syscall_exit_probe, NULL);


	printk(KERN_INFO "syscall_hypertracing: init module.\n");
	return 0;
}


static void __exit syscall_hypertracing_cleanup(void) {
	printk(KERN_INFO "syscall_hypertracing: removing module.\n");
    tracepoint_probe_unregister(tp_sysenter, syscall_entry_probe, NULL);
	tracepoint_probe_unregister(tp_sysexit, syscall_exit_probe, NULL);
}


module_init(syscall_hypertracing_init);
module_exit(syscall_hypertracing_cleanup);