
echo function_graph > /sys/kernel/debug/tracing/current_tracer
echo 0 > /sys/kernel/debug/tracing/tracing_on
echo 100000 > /sys/kernel/debug/tracing/buffer_size_kb
echo funcgraph-tail > /sys/kernel/debug/tracing/trace_options
echo funcgraph-abstime > /sys/kernel/debug/tracing/trace_options

echo 0 > /sys/kernel/debug/tracing/tracing_on
echo > /sys/kernel/debug/tracing/trace
echo > /sys/kernel/debug/tracing/set_graph_function
echo > /sys/kernel/debug/tracing/set_ftrace_filter

# echo vmx_vcpu_run > /sys/kernel/debug/tracing/set_graph_function
echo vmx_vcpu_run > /sys/kernel/debug/tracing/set_ftrace_filter
echo handle_vmcall >> /sys/kernel/debug/tracing/set_ftrace_filter
echo vmx_handle_exit >> /sys/kernel/debug/tracing/set_ftrace_filter
echo vmx_save_host_state >> /sys/kernel/debug/tracing/set_ftrace_filter
# echo vmx_arm_hv_timer >> /sys/kernel/debug/tracing/set_ftrace_filter
# echo vmx_complete_atomic_exit* > /sys/kernel/debug/tracing/set_ftrace_filter
echo vmx_complete_interrupts >> /sys/kernel/debug/tracing/set_ftrace_filter

echo 0 > /sys/kernel/debug/tracing/events/kvm/enable
# echo 1 > /sys/kernel/debug/tracing/events/kvm/kvm_nested_vmexit_inject/enable
echo 1 > /sys/kernel/debug/tracing/events/kvm/kvm_exit/enable
echo 1 > /sys/kernel/debug/tracing/events/kvm/kvm_entry/enable
echo 1 > /sys/kernel/debug/tracing/tracing_on
ssh vm '/home/abder/hypercall_guest'
# sleep 1
echo 0 > /sys/kernel/debug/tracing/tracing_on

cat /sys/kernel/debug/tracing/trace > ftrace-trace.txt
echo nop > /sys/kernel/debug/tracing/current_tracer