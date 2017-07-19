
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
static struct tracepoint *tp_sched_switch;
static void set_tracepoint(struct tracepoint *tp, void *priv) {
	//printk(KERN_INFO "trace point %s\n", tp->name);
	if (strcmp(tp->name, "sys_enter") == 0)
		tp_sysenter = tp;

	if (strcmp(tp->name, "sys_exit") == 0)
		tp_sysexit = tp;

	if (strcmp(tp->name, "sched_switch") == 0)
		tp_sched_switch = tp;
}

static void probe_sched_switch(void *ignore, bool preempt,
           struct task_struct *prev, struct task_struct *next)
{
    /*
     * Do hypercall to send sched_switch event to host
     */
      do_hypercall(1002,
                 prev->pid,
                 prev->tgid,
                 next->pid,
                 next->tgid);
}
//*****************************************************
// Syscall filtering
//*****************************************************
void syscall_entry_probe(void *__data, struct pt_regs *regs, long id)
{
	switch (id) 
	{
		case 0:
		case 1:
		case 2:
		case 3:
			// printk(KERN_INFO "hypertracing %u: syscall entry id=%d\n", current->pid, id);
			do_hypercall(4000, id, 0, 0, 0);
			break;
		default:
			break;
	}	
}

void syscall_exit_probe(void *__data, struct pt_regs *regs, long ret)
{
	long id;

	// printk(KERN_INFO "hypertracing %u: syscall exit ret=%d\n", current->pid, ret);
	id = syscall_get_nr(current, regs);

	switch (id) 
	{
		case 0:
		case 1:
		case 2:
		case 3:
			// printk(KERN_INFO "hypertracing %u: syscall exit ret=%d\n", current->pid, ret);
			do_hypercall(4000, id, 1, ret, 0);
			break;
		default:
			break;
	}	
}
//*****************************************************
// module init/exit
//*****************************************************

//extern struct nsproxy init_nsproxy;
static int __init io_hypertracing_init(void) {
	int ret;

	for_each_kernel_tracepoint(set_tracepoint, NULL);
	if (tp_sysenter == NULL) {
		printk(KERN_INFO "io_hypertracing: failed to find tracepoints.\n");
		return 1;
	}
	ret = tracepoint_probe_register(tp_sysenter, syscall_entry_probe, NULL);

	if (ret) {
		printk(KERN_INFO "io_hypertracing: failed initializing syscall_entry_probe.\n");
		return 1;
	}

	if (tp_sysenter == NULL) {
		printk(KERN_INFO "io_hypertracing: failed to find tracepoints.\n");
		return 1;
	}
	ret = tracepoint_probe_register(tp_sysexit, syscall_exit_probe, NULL);

	if (tp_sched_switch == NULL) {
		printk(KERN_INFO "io_hypertracing: failed to find tracepoints.\n");
		return 1;
	}
	ret = tracepoint_probe_register(tp_sched_switch, probe_sched_switch, NULL);


	printk(KERN_INFO "io_hypertracing: init module.\n");
	return 0;
}


static void __exit io_hypertracing_cleanup(void) {
	printk(KERN_INFO "io_hypertracing: removing module.\n");
	tracepoint_probe_unregister(tp_sysenter, syscall_entry_probe, NULL);
	tracepoint_probe_unregister(tp_sysexit, syscall_exit_probe, NULL);
	tracepoint_probe_unregister(tp_sched_switch, probe_sched_switch, NULL);
}


module_init(io_hypertracing_init);
module_exit(io_hypertracing_cleanup);