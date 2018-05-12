
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
static struct tracepoint *tp_sched_process_exit;
static struct tracepoint *tp_sched_migrate_task;
static struct tracepoint *tp_sched_process_fork;
static struct tracepoint *tp_sched_switch;

static void set_tracepoint(struct tracepoint *tp, void *priv) {
	//printk(KERN_INFO "trace point %s\n", tp->name);
	if (strcmp(tp->name, "sched_process_exit") == 0)
		tp_sched_process_exit = tp;
		
	if (strcmp(tp->name, "sched_migrate_task") == 0)
		tp_sched_migrate_task = tp;

	if (strcmp(tp->name, "sched_process_fork") == 0)
		tp_sched_process_fork = tp;

	if (strcmp(tp->name, "sched_switch") == 0)
		tp_sched_switch = tp;
}

static void probe_sched_switch(void *ignore, bool preempt,
           struct task_struct *prev, struct task_struct *next)
{
	do_hypercall(0x01, prev->pid, prev->tgid, next->pid,next->tgid);
}

static void probe_sched_migrate_task(void *ignore, struct task_struct *p, unsigned int dest_cpu)
{
	do_hypercall(0x02, p->pid, p->tgid, dest_cpu, 0);
}

static void probe_sched_process_exit(void *ignore, struct task_struct *tsk)
{
	do_hypercall(0x03, tsk->pid, tsk->tgid, 0, 0);
}

static void probe_sched_process_fork(void *ignore, struct task_struct *parent, struct task_struct *child)
{
	do_hypercall(0x04, parent->pid, parent->tgid, child->pid, child->tgid);
}

//*****************************************************
// module init/exit
//*****************************************************

//extern struct nsproxy init_nsproxy;
static int __init cpu_hypertracing_init(void) {
	int ret;

	for_each_kernel_tracepoint(set_tracepoint, NULL);

    // tp_sched_switch
	if (tp_sched_switch == NULL) {
		printk(KERN_INFO "cpu_hypertracing: failed to find tracepoints.\n");
		return 1;
	}
	ret = tracepoint_probe_register(tp_sched_switch, probe_sched_switch, NULL);

    // tp_sched_migrate_task
    if (tp_sched_migrate_task == NULL) {
		printk(KERN_INFO "cpu_hypertracing: failed to find tracepoints.\n");
		return 1;
	}
	ret = tracepoint_probe_register(tp_sched_migrate_task, probe_sched_migrate_task, NULL);

	// tp_sched_process_exit
    if (tp_sched_process_exit == NULL) {
		printk(KERN_INFO "cpu_hypertracing: failed to find tracepoints.\n");
		return 1;
	}
	ret = tracepoint_probe_register(tp_sched_process_exit, probe_sched_process_exit, NULL);

	// tp_sched_process_fork
    if (tp_sched_process_fork == NULL) {
		printk(KERN_INFO "cpu_hypertracing: failed to find tracepoints.\n");
		return 1;
	}
	ret = tracepoint_probe_register(tp_sched_process_fork, probe_sched_process_fork, NULL);

	printk(KERN_INFO "cpu_hypertracing: init module.\n");
	return 0;
}


static void __exit cpu_hypertracing_cleanup(void) {
	printk(KERN_INFO "cpu_hypertracing: removing module.\n");

	tracepoint_probe_unregister(tp_sched_switch, probe_sched_switch, NULL);
	tracepoint_probe_unregister(tp_sched_migrate_task, probe_sched_migrate_task, NULL);
	tracepoint_probe_unregister(tp_sched_process_exit, probe_sched_process_exit, NULL);
	tracepoint_probe_unregister(tp_sched_process_fork, probe_sched_process_fork, NULL);
}


module_init(cpu_hypertracing_init);
module_exit(cpu_hypertracing_cleanup);