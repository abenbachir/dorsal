/*
 *
 * Function hypergraph
 *
 * Copyright (C) 2017 Abderrahmane Benbachir <abderrahmane.benbachir@polymtl.ca>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; only
 * version 2.1 of the License.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 *
 */
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/ftrace.h>
#include <linux/printk.h>
#include <linux/kallsyms.h>
#include <linux/types.h>
#include <linux/preempt.h>
#include <linux/tracepoint.h>
#include <linux/proc_fs.h>
#include <asm-generic/uaccess.h>
#include <linux/slab.h>

#define SCHED_SWITCH_HYPERCALL_NR 1001
#define HYPERCALL_NR 1000
#define FUNCTION_ENTRY 0
#define FUNCTION_EXIT 1

#define do_hypercall(nr, p1, p2, p3, p4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), \
	"b"(p1), \
	"c"(p2), \
	"d"(p3), \
	"S"(p4))

static int tracing_enabled = 0;

struct Query {
	struct tracepoint *tp;
	const char *name;
} query;


static int (*register_ftrace_graph_sym)(trace_func_graph_ret_t retfunc, trace_func_graph_ent_t entryfunc);
static void (*unregister_ftrace_graph_sym)(void);


static void notrace find_for_each_tracepoint(struct tracepoint *tp, void *priv)
{
	struct Query *q = priv;
	if (strcmp(tp->name, q->name) == 0) {
		q->tp = tp;
	}
}

static void notrace sched_switch_probe(void *ignore, bool preempt,
		   struct task_struct *prev, struct task_struct *next)
{
	if(!tracing_enabled)
		return;
	preempt_disable_notrace();
	int cpu = smp_processor_id();
	do_hypercall(SCHED_SWITCH_HYPERCALL_NR, prev->pid, prev->tgid, next->pid, next->tgid);
	// printk("sched_switch_probe : prev_pid=%d prev_tgid=%d next_pid=%d next_tgid=%d\n", prev->pid, prev->tgid, next->pid, next->tgid);
	preempt_enable_notrace();
}

// called by prepare_ftrace_return()
// The corresponding return hook is called only when this function returns 1
static int notrace hypergraph_entry(struct ftrace_graph_ent *trace)
{
	int ret = 1;
	int cpu = 0;
	// For now, only trace normal context
	if (in_interrupt())
		return 0;
	if(!tracing_enabled)
		return 0;
	// check recursion
	preempt_disable_notrace();

	// record event :
	cpu = smp_processor_id();
	do_hypercall(HYPERCALL_NR, trace->func, FUNCTION_ENTRY, cpu, trace->depth);
	// atomic_inc(&entries);

	preempt_enable_notrace();
	return ret;
}

// called by ftrace_return_to_handler()
static void notrace hypergraph_return(struct ftrace_graph_ret *trace)
{
	if(!tracing_enabled)
		return 0;
	preempt_disable_notrace();
	// record event : 	
	do_hypercall(HYPERCALL_NR, trace->func, FUNCTION_EXIT, (trace->rettime - trace->calltime), trace->depth);
	// atomic_inc(&returns);
	preempt_enable_notrace();
	return;
}
 
static ssize_t notrace proc_read(struct file *filp, char *buf, size_t count, loff_t *offp)
{	
	printk(KERN_INFO "proc called read\n");
	int size = 17;
	char mybuf[] = "Tracing disabled\n";
	//sprintf(mybuf, "Tracing %s \n", tracing_enabled ? "enabled" : "disabled"); 
	printk(KERN_INFO "%s\n", mybuf);
	copy_from_user(buf,mybuf,size);
	return size;
}

static ssize_t notrace proc_write(struct file *filp, const char __user *buf, size_t count, loff_t *offp)
{
	char mybuf[count];
	printk(KERN_INFO "proc called write\n");

	copy_from_user(mybuf,buf,count);
	tracing_enabled = (count > 1 && mybuf[0] == '1');
	
	printk("Tracing %s \n", tracing_enabled ? "enabled" : "disabled");

	return count;
} 
static int proc_open(struct inode * sp_inode, struct file *sp_file)
{
	printk(KERN_INFO "proc called open\n");
	return 0;
}
static int proc_release(struct inode *sp_indoe, struct file *sp_file)
{
	printk(KERN_INFO "proc called release\n");
	return 0;
}

struct file_operations proc_fops = {
	.open = proc_open,
	.read = proc_read,
	.write = proc_write,
	.release = proc_release	
};


static int __init hypergraph_init(void)
{
	int ret;

	proc_create("hypergraph", 0666, NULL, &proc_fops);

	query.tp = NULL;
	query.name = "sched_switch";

	for_each_kernel_tracepoint(find_for_each_tracepoint, &query);
	ret = tracepoint_probe_register(query.tp, sched_switch_probe, NULL);
	if(ret){
		printk("register sched_switch hooks failed ret=%d\n", ret);
		tracepoint_probe_unregister(query.tp, sched_switch_probe, NULL);
		goto out;
	}
	printk("tracepoint found: %p %s\n", query.tp, query.tp ? query.tp->name : "null");

	register_ftrace_graph_sym = (void *) kallsyms_lookup_name("register_ftrace_graph");
	unregister_ftrace_graph_sym = (void *) kallsyms_lookup_name("unregister_ftrace_graph");

	printk("register=%p unregister=%p\n", register_ftrace_graph_sym,
			unregister_ftrace_graph_sym);

	if (!register_ftrace_graph_sym ||
	    !unregister_ftrace_graph_sym) {
		printk("hypergraph init failed\n");
		return -1;
	}

	ret = register_ftrace_graph_sym(hypergraph_return, hypergraph_entry);
	if (ret) {
		printk("register hypergraph hooks failed ret=%d\n", ret);
		goto out;
	}

	printk("hypergraph loaded\n");

out:
	return ret;
}
module_init(hypergraph_init);

static void __exit hypergraph_exit(void)
{
	remove_proc_entry("hypergraph", NULL);

	unregister_ftrace_graph_sym();
	tracepoint_probe_unregister(query.tp, sched_switch_probe, NULL);
	synchronize_rcu();

	printk("hypergraph removed\n");
}
module_exit(hypergraph_exit);

MODULE_LICENSE("GPL and additional rights");
MODULE_AUTHOR("Abder Benbachir <abderrahmane.benbachir@polymtl.ca>");
MODULE_DESCRIPTION("Function hypergraph");
MODULE_VERSION("1.0");
