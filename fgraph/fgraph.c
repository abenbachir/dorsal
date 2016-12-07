/*
 * ftrace.c
 *
 * Function hypergraph
 *
 * Copyright (C) 2016 Mathieu Desnoyers <mathieu.desnoyers@efficios.com>
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

#include <linux/module.h>
#include <linux/ftrace.h>
#include <linux/printk.h>
#include <linux/kallsyms.h>
#include <linux/types.h>
#include <linux/preempt.h>
#include <linux/tracepoint.h>

#define SCHED_SWITCH_HYPERCALL_NR 1001
#define HYPERCALL_NR 1000
#define FUNCTION_ENTRY 0
#define FUNCTION_EXIT 1

#define do_hypercall(hypercall_nr, arg1, arg2, arg3, arg4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), \
	"b"(arg1), \
	"c"(arg2), \
	"d"(arg3), \
	"S"(arg4))

struct Query {
	struct tracepoint *tp;
	const char *name;
} query;



static int (*register_ftrace_graph_sym)(trace_func_graph_ret_t retfunc, trace_func_graph_ent_t entryfunc);
static void (*unregister_ftrace_graph_sym)(void);

static atomic_t entries = ATOMIC_INIT(0);
static atomic_t returns = ATOMIC_INIT(0);

static void notrace find_for_each_tracepoint(struct tracepoint *tp, void *priv)
{
	struct Query *q = priv;
	if (strcmp(tp->name, q->name) == 0) {
		q->tp = tp;
	}
}

static void notrace sched_switch_probe(void *__data, struct task_struct *p, int success)
{
	preempt_disable_notrace();
	// if(p)
	// 	do_hypercall(SCHED_SWITCH_HYPERCALL_NR, success, p->state, 0, 0);
	int cpu = smp_processor_id();
	do_hypercall(SCHED_SWITCH_HYPERCALL_NR, success, cpu, 0, 0);
	preempt_enable_notrace();
}

// called by prepare_ftrace_return()
// The corresponding return hook is called only when this function returns 1
static int notrace fgraph_entry(struct ftrace_graph_ent *trace)
{
	int ret = 1;
	int cpu = 0;
	// For now, only trace normal context
	if (in_interrupt())
		return 0;
	// check recursion
	preempt_disable_notrace();

	// record event :
	cpu = smp_processor_id();
	do_hypercall(HYPERCALL_NR, trace->func, FUNCTION_ENTRY, 0, cpu);
	// atomic_inc(&entries);

	preempt_enable_notrace();
	return ret;
}

// called by ftrace_return_to_handler()
static void notrace fgraph_return(struct ftrace_graph_ret *trace)
{
	preempt_disable_notrace();
	// record event : 	
	do_hypercall(HYPERCALL_NR, trace->func, FUNCTION_EXIT, (trace->rettime - trace->calltime), trace->depth);
	// atomic_inc(&returns);
	preempt_enable_notrace();
	return;
}

static int __init fgraph_init(void)
{
	int ret;

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
		printk("fgraph init failed\n");
		return -1;
	}

	ret = register_ftrace_graph_sym(fgraph_return, fgraph_entry);
	if (ret) {
		printk("register fgraph hooks failed ret=%d\n", ret);
		goto out;
	}

	printk("fgraph loaded\n");

out:
	return ret;
}
module_init(fgraph_init);

static void __exit fgraph_exit(void)
{
	// unregister ftrace
	unregister_ftrace_graph_sym();
	// unregister sched_switch
	tracepoint_probe_unregister(query.tp, sched_switch_probe, NULL);
	synchronize_rcu();

	printk("fgraph removed\n");
}
module_exit(fgraph_exit);

MODULE_LICENSE("GPL and additional rights");
MODULE_AUTHOR("Abder Benbachir <anis.benbachir@gmail.com>");
MODULE_DESCRIPTION("Function hypergraph");
MODULE_VERSION("1.0");
