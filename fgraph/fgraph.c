/*
 * ftrace.c
 *
 * Function graph
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
// #include <wrapper/ftrace.h>
// #include <wrapper/tracepoint.h>
// #include <wrapper/vmalloc.h>
#include <linux/types.h>
#include <linux/list.h>
#include <linux/preempt.h>

#define HYPERCALL_NR 11
#define FUNCTION_ENTRY 0
#define FUNCTION_EXIT 1

#define do_hypercall(hypercall_nr, arg1, arg2, arg3, arg4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), \
	"b"(arg1), \
	"c"(arg2), \
	"d"(arg3), \
	"S"(arg4))


static int (*register_ftrace_graph_sym)(trace_func_graph_ret_t retfunc,
			trace_func_graph_ent_t entryfunc);
static void (*unregister_ftrace_graph_sym)(void);


static atomic_t entries = ATOMIC_INIT(0);
static atomic_t returns = ATOMIC_INIT(0);

// called by prepare_ftrace_return()
// The corresponding return hook is called only when this function returns 1
int notrace fgraph_entry(struct ftrace_graph_ent *trace)
{
	int ret = 0;

	// For now, only trace normal context
	if (in_interrupt())
		return 0;

	// check recursion
	preempt_disable_notrace();

	// record event : do hypercall

	do_hypercall(HYPERCALL_NR, trace->func, FUNCTION_ENTRY, 0, 0);
	atomic_inc(&entries);

	preempt_enable_notrace();
	return ret;
}

// called by ftrace_return_to_handler()
void notrace fgraph_return(struct ftrace_graph_ret *trace)
{
	preempt_disable_notrace();

	// record event : do hypercall
	do_hypercall(HYPERCALL_NR, trace->func, FUNCTION_EXIT, (trace->rettime - trace->calltime), 0);
	atomic_inc(&returns);

	preempt_enable_notrace();
	return;
}

static int __init fgraph_init(void)
{
	int ret;

	register_ftrace_graph_sym = (void *) kallsyms_lookup_name("register_ftrace_graph");
	unregister_ftrace_graph_sym = (void *) kallsyms_lookup_name("unregister_ftrace_graph");

	printk("register=%p unregister=%p\n", register_ftrace_graph_sym,
			unregister_ftrace_graph_sym);

	if (!register_ftrace_graph_sym ||
	    !unregister_ftrace_graph_sym) {
		printk("fgraph init failed\n");
		return -1;
	}

	// parent_sym = kallsyms_lookup_funcptr("do_sys_open");
	// if (!parent_sym) {
	// 	printk("kallsyms lookup failed\n");
	// 	return -1;
	// }

	ret = register_ftrace_graph_sym(fgraph_return, fgraph_entry);
	if (ret) {
		printk("register fgraph hooks failed ret=%d\n", ret);
		return -1;
	}

	// ret = __lttng_events_init__fgraph();
	if (ret)
		return -1;

	printk("fgraph loaded\n");
	return 0;
}
module_init(fgraph_init);

static void __exit fgraph_exit(void)
{
	unregister_ftrace_graph_sym();
	synchronize_rcu();
	// __lttng_events_exit__fgraph();
	printk("fgraph removed\n");
	printk("entries=%d returns=%d\n", atomic_read(&entries),
			atomic_read(&returns));
}
module_exit(fgraph_exit);

MODULE_LICENSE("GPL and additional rights");
MODULE_AUTHOR("Francis Giraldeau <francis.giraldeau@gmail.com>");
MODULE_DESCRIPTION("Function graph");
MODULE_VERSION("1.0");
