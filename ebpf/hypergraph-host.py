#!/usr/bin/env python
# Copyright (c) PLUMgrid, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")

# This is an example of tracing an event and printing custom fields.
# run in project examples directory with:
# sudo ./trace_fields.py"

import atexit
from bcc import BPF
import ctypes as ct
from pprint import pprint

class KVM_DATA(ct.Structure):
    _fields_ = [
        ("start", ct.c_ubyte),
        ("exit_reason", ct.c_ubyte),
        ("isa", ct.c_uint),
        ("nr", ct.c_ulonglong),
        ("a0", ct.c_ulonglong),
        ("a1", ct.c_ulonglong),
        ("a2", ct.c_ulonglong),
        ("a3", ct.c_ulonglong),
        ("vcpu_id", ct.c_ulonglong),
        ("overhead", ct.c_ulonglong)
    ]
    def __str__(self):
        value = ""
        attrs = [x for x in dir(self) if not x.startswith('_')]
        for attr in attrs:
           value += "%s=%s, " % (attr, getattr(self, attr))
        value += '\n'
        return value

counter = 0

def cb(cpu, data, size):
    assert size >= ct.sizeof(KVM_DATA)
    global counter
    counter += 1
    # event = ct.cast(data, ct.POINTER(KVM_DATA)).contents

    # print("[%0d] %s" % (cpu, event))


prog = """
#include <linux/sched.h>

#define EXIT_REASON 18
struct kvm_data {
    u8 start;
    u8 exit_reason;
    u32 isa;
    u64 nr;
    u64 a0;
    u64 a1;
    u64 a2;
    u64 a3;
    u64 vcpu_id;
    u64 overhead;
};

BPF_PERF_OUTPUT(events);
BPF_ARRAY(kvm_data_list, struct kvm_data, 16);

TRACEPOINT_PROBE(kvm, kvm_exit) {
    int rc;    
    /*if (args->exit_reason == EXIT_REASON) {
        int cpu_id = bpf_get_smp_processor_id();
        struct kvm_data* data_ptr = kvm_data_list.lookup(&cpu_id);
        if(!data_ptr)
            return 0;
        
        data_ptr->start = 1;
        data_ptr->isa = args->isa;
        data_ptr->exit_reason = args->exit_reason;
        data_ptr->overhead = bpf_ktime_get_ns();
    }*/
    
    
    return 0;
}

TRACEPOINT_PROBE(kvm, kvm_hypercall) {
    /*int cpu_id = bpf_get_smp_processor_id();
    struct kvm_data* data_ptr = kvm_data_list.lookup(&cpu_id);
    if(!data_ptr)
        return 0;
    
    if(data_ptr->start <= 0)
        return 0;

    data_ptr->nr = args->nr;
    data_ptr->a0 = args->a0;
    data_ptr->a1 = args->a1;
    data_ptr->a2 = args->a2;
    data_ptr->a3 = args->a3;*/
    return 0;
}

TRACEPOINT_PROBE(kvm, kvm_entry) {
        
    /*int cpu_id = bpf_get_smp_processor_id();
    struct kvm_data* data_ptr = kvm_data_list.lookup(&cpu_id);
    if(!data_ptr)
        return 0;
    
    if(data_ptr->start <= 0)
        return 0;

    data_ptr->overhead = bpf_ktime_get_ns() - data_ptr->overhead;
    data_ptr->start = 0;
    data_ptr->vcpu_id = args->vcpu_id;
*/
    int rc;
    /*struct kvm_data event = *data_ptr;
    if ((rc = events.perf_submit(args, &event, sizeof(event))) < 0)
        bpf_trace_printk("perf_output failed: %d\\n", rc);*/

    return 0;
};

"""
b = BPF(text=prog)
b["events"].open_perf_buffer(cb)


print("Tracing sys_write, try `dd if=/dev/zero of=/dev/null`")
print("Tracing... Hit Ctrl-C to end.")
while 1:
    b.kprobe_poll()

global counter
print('counter=%s'%counter)