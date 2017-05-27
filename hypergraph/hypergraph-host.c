/*
 *
 * hypergraph host module : Hook to kvm probe entry exit and hypercall
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
#include <linux/printk.h>
#include <linux/kallsyms.h>
#include <linux/types.h>
#include <linux/string.h>
#include <linux/preempt.h>
#include <linux/tracepoint.h>
#include <linux/slab.h>
#include <linux/kvm_host.h>
#include <../arch/x86/kvm/kvm_cache_regs.h>

#define HYPERCALL_EXIT_REASON 18

struct tracepoint_entry {
	void *probe;
	const char *name;
	struct tracepoint *tp;	
};

static int hypergraph_tracepoint_notify(struct notifier_block *self, unsigned long val, void *data);
static void kvm_exit_handler(void *__data, unsigned int exit_reason, struct kvm_vcpu *vcpu, u32 isa);
static void kvm_hypercall_handler(void *__data, unsigned long nr,
		unsigned long a0, unsigned long a1, unsigned long a2, unsigned long a3);
static void kvm_entry_handler(void *__data, unsigned int vcpu_id);

static unsigned int start = 0;

static struct notifier_block hypergraph_tracepoint_notifier = {
	.notifier_call = hypergraph_tracepoint_notify,
	.priority = 0,
};
static struct tracepoint_entry tracepoint_table[] = {
	{ .name = "kvm_entry", 		.probe = kvm_entry_handler },
	{ .name = "kvm_exit", 		.probe = kvm_exit_handler },
	{ .name = "kvm_hypercall", 	.probe = kvm_hypercall_handler }
};
static size_t TABLE_SIZE = sizeof(tracepoint_table) / sizeof(tracepoint_table[0]);

static
void kvm_exit_handler(void *__data, unsigned int exit_reason, struct kvm_vcpu *vcpu, u32 isa)
{
	unsigned long guest_rip = kvm_rip_read(vcpu);
	if (exit_reason == HYPERCALL_EXIT_REASON){
		start = 1;
		printk("kvm_exit exit_reason=%u, guest_rip=%lu, isa=%u\n", exit_reason, guest_rip, isa);
	}
}

static
void kvm_hypercall_handler(void *__data, unsigned long nr,
		unsigned long a0, unsigned long a1, unsigned long a2, unsigned long a3)
{
	if(start > 0){
		printk("kvm_hypercall nr=%lu, a0=%lu, a1=%lu, a2=%lu, a3=%lu\n", nr, a0, a1, a2, a3);
	}
}

static
void kvm_entry_handler(void *__data, unsigned int vcpu_id)
{	
	if(start > 0){
		start = 0;
		printk("kvm_entry vcpu_id=%d\n", vcpu_id);
	}
}

static int hypergraph_tracepoint_probe_register(struct tracepoint_entry *entry)
{
	int ret = 0;

	if(entry->tp == NULL){
		printk("register %s hooks failed, tracepoint not found\n", entry->name);
		return -EINVAL;
	}

	ret = tracepoint_probe_register(entry->tp, entry->probe, NULL);
	if(ret){
		printk("register %s hooks failed ret=%d\n", entry->name, ret);
		tracepoint_probe_unregister(entry->tp, entry->probe, NULL);
		return ret;
	}

	printk("tracepoint found: %p %s\n", entry->tp, entry->tp ? entry->tp->name : "null");
	return ret;
}

static void hypergraph_tracepoint_probe_unregister(struct tracepoint_entry *entry)
{
	if(entry == NULL)
		return;
	if(entry->tp == NULL || entry->probe == NULL)
		return;

	printk("%s probe was unregistered\n", entry->name);
	tracepoint_probe_unregister(entry->tp, entry->probe, NULL);
}

static
int hypergraph_tracepoint_coming(struct tp_module *tp_mod)
{
	int i, j, ret = 0;

	for (i = 0; i < tp_mod->mod->num_tracepoints; i++) {
		struct tracepoint *tp;
		tp = tp_mod->mod->tracepoints_ptrs[i];	
		
		// register probes if they match
		for(j = 0; j < TABLE_SIZE; j++) {
			if (strcmp(tp->name, tracepoint_table[j].name) == 0) {
				tracepoint_table[j].tp = tp;
				ret = hypergraph_tracepoint_probe_register(&tracepoint_table[j]);
			}
		}		
	}
	return ret;
}

static
int hypergraph_tracepoint_notify(struct notifier_block *self,
		unsigned long val, void *data)
{
	struct tp_module *tp_mod = data;
	int ret = 0;

	switch (val) {
		case MODULE_STATE_COMING:
			ret = hypergraph_tracepoint_coming(tp_mod);
			break;
		case MODULE_STATE_GOING:
			// ...
			break;
		default:
			break;
	}
	return ret;
}


static int __init hypergraph_init(void)
{
	int ret;

	ret = register_tracepoint_module_notifier(&hypergraph_tracepoint_notifier);
	if(ret)
		return ret;

	printk("hypergraph-host module loaded\n");
	return ret;
}
module_init(hypergraph_init);

static void __exit hypergraph_exit(void)
{
	int i;
	for(i = 0; i < TABLE_SIZE; i++)
		hypergraph_tracepoint_probe_unregister(&tracepoint_table[i]);

	// synchronize_rcu();
	unregister_tracepoint_module_notifier(&hypergraph_tracepoint_notifier);
	
	printk("hypergraph-host module removed\n");
}
module_exit(hypergraph_exit);

MODULE_LICENSE("GPL and additional rights");
MODULE_AUTHOR("Abderrahmane Benbachir <abderrahmane.benbachir@polymtl.ca>");
MODULE_DESCRIPTION("Hypergraph host handler");
MODULE_VERSION("1.0");
