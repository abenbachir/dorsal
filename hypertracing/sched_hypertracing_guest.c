
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
//sched_switch,sched_migrate_task,sched_process_fork,sched_process_exit

static struct tracepoint *tp_sched_switch;

static void set_tracepoint(struct tracepoint *tp, void *priv) {
	//printk(KERN_INFO "trace point %s\n", tp->name);

	if (strcmp(tp->name, "sched_switch") == 0)
		tp_sched_switch = tp;
}

static void probe_sched_switch(void *ignore, bool preempt,
           struct task_struct *prev, struct task_struct *next)
{
	do_hypercall(0x01, prev->pid, prev->tgid, next->pid,next->tgid);
}


//*****************************************************
// module init/exit
//*****************************************************

//extern struct nsproxy init_nsproxy;
static int __init sched_hypertracing_init(void) {
	int ret;

	for_each_kernel_tracepoint(set_tracepoint, NULL);

    // tp_sched_switch
	if (tp_sched_switch == NULL) {
		printk(KERN_INFO "sched_hypertracing: failed to find tracepoints.\n");
		return 1;
	}
	ret = tracepoint_probe_register(tp_sched_switch, probe_sched_switch, NULL);

	printk(KERN_INFO "sched_hypertracing: init module.\n");
	return 0;
}


static void __exit sched_hypertracing_cleanup(void) {
	printk(KERN_INFO "sched_hypertracing: removing module.\n");

	tracepoint_probe_unregister(tp_sched_switch, probe_sched_switch, NULL);
}


module_init(sched_hypertracing_init);
module_exit(sched_hypertracing_cleanup);