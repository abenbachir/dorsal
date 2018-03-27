
bzImage=/home/abder/linux-bootlevel/arch/x86/boot/bzImage
bzImage_baseline=/home/abder/linux-baseline/arch/x86/boot/bzImage
bzImage_full_config=/home/abder/linux-vm-full-config/arch/x86/boot/bzImage
bzImage_from_hdd=/media/abder/external-drive/linux-vm/arch/x86/boot/bzImage
bzImage_shutdown=/home/abder/linux-vm-shutdown/arch/x86/boot/bzImage
qcow2=/var/lib/libvirt/images/VM.qcow2
qemu_exe=/home/abder/jkqemu/x86_64-softmmu/qemu-system-x86_64
# param="ftrace=function ftrace_dump_on_oops ftrace_vearly ftrace_filter=*_init ftrace_notrace=read_pci*,e820*,acpi_*,native_flush_*,*_fixmap*,early_mem*,*early_io*,__probe*,*print*,console*,mutex*,jump_label*,arch_jump*,*raw_spin*,get_page_bootmem,*free*,*mod_zone*,parame*"
# param="ftrace=function ftrace_dump_on_oops ftrace_vearly ftrace_filter=*_init"
# param="ftrace=function ftrace_dump_on_oops ftrace_vearly ftrace_filter=*_init ftrace_notrace=print*,*mutex*"

param="boot1 trace_bootlevel_end=1 trace_initcall print_initcall"
#param="trace_boot1 trace_bootlevel_end=1  trace_initcall inject_latency=0"
#param="trace_boot1 trace_bootlevel_end=1"

# 	-serial stdio -hda $qcow2 \
# 
run_qemu()
{
	p1=$1
	affinity=$2
	image=$3

	sudo taskset -c $affinity qemu-system-x86_64 \
	-m 2048 -smp 1 -M pc -name guest_$affinity \
	-enable-kvm -append "root=/dev/sda1 console=tty0 console=ttyS0 rw $p1" \
	--kernel $image \
	-serial stdio \
	&
}
run_qemu_2()
{
	param=$1
	vcpunum=$2
	affinity=$3
	sudo $qemu_exe \
	-m 2048 -smp 1 -M pc -name guest_$affinity \
	-vcpu vcpunum=$vcpunum,affinity=$affinity \.
	-serial stdio -hda $qcow2 \
	-enable-kvm -append "root=/dev/sda1 console=tty0 console=ttyS0 rw $param" \
	--kernel $bzImage \
	&
}

run_qemu_default()
{
	run_qemu "${param}" "${1}" "${bzImage}"
}
run_qemu_from_hdd()
{
	run_qemu "${param}" "${1}" "${bzImage_from_hdd}"
}
run_qemu_full_config()
{
	run_qemu "${param}" "${1}" "${bzImage_full_config}"
}



trace_1_vm()
{
	run_qemu_default 1
	sleep 5
}

trace_5_vms()
{
	run_qemu_default 1
	run_qemu_default 2
	run_qemu_default 3
	run_qemu_default 4
	run_qemu_default 5
	sleep 10
}
trace_multiple_vms()
{
	run_qemu_default 1
	run_qemu_default 2
	run_qemu_default 3
	run_qemu_default 4
	run_qemu_default 5
	run_qemu_default 6
	run_qemu_default 7
	sleep 10
}

trace_2_vms_on_same_cpu()
{
	run_qemu_default 1
	run_qemu_default 1
	run_qemu_default 5
	sleep 5
}

trace_vm_full_vs_small_kernel()
{
	run_qemu_default 2
#	run_qemu_full_config 5
	run_qemu_ubuntu_config 7
	sleep 5
}

trace_ssd_vs_hdd_vms()
{
	run_qemu_default 2
	run_qemu_from_hdd 5
	sleep 5
}

trace_use_cases()
{
	# full vs small
	run_qemu_full_config 7

	# same CPU
	run_qemu_default 5
	run_qemu_default 5

	run_qemu_default 2
	run_qemu_default 1

	# with latency module
	param2="trace_boot1 trace_bootlevel_end=1  trace_initcall inject_latency=800"
	run_qemu "${param2}" 3 "${bzImage}"
}

lttng_start()
{
	output="/home/abder/lttng-traces/bootup-benchmark"
	rm -rf $output
	lttng create bootup-benchmark --output="$output"
	lttng enable-channel -k --subbuf-size=128K --num-subbuf=64 vm_channel
	# lttng enable-event -k "kvm_x86_entry,kvm_x86_exit,kvm_x86_hypercall" -c vm_channel
	lttng enable-event -k "kvm_x86_write_tsc_offset,kvm_x86_hypercall" -c vm_channel
	# lttng add-context -k -t pid -t tid -t procname -c vm_channel
	lttng start 

	# param="trace_boot1 trace_bootlevel_end=1 trace_initcall"
	# param="trace_boot1 trace_bootlevel_end=1"
	# param="initcall_debug"
	# param="ftrace=function_graph ftrace_dump_on_oops ftrace_graph_filter=do_one_initcall ftrace_notrace=debugfs*,kmem_*,*initcall* ftrace_graph_max_depth=2"
	param=""

	#run_qemu "${param}" 7 "${bzImage_baseline}"
	run_qemu "" 5 "${bzImage_baseline}"

	#taskset -c 5 virsh start VM1

	sleep 2

	lttng stop
	lttng view | wc -l
	lttng destroy

	./boot-time.py $output
}

# run_qemu "" 1 "${bzImage}"

filter_notrace="ftrace_notrace=read_pci*,e820*,acpi_*,native_flush_*,*_fixmap*,early_mem*,*early_io*,__probe*,*print*,console*,mutex*,jump_label*,arch_jump*,*raw_spin*,get_page_bootmem,*free*,*mod_zone*,parame*"
param2="ftrace_dump_on_oops ftrace_vearly ftrace=function trace_buf_size=40M ftrace_filter=*_init $filter_notrace"

run_qemu "${param2}" 3 "${bzImage}"

	# pr_info("[DEBUG] %d,%s, first=%pS,last=%pS\n", level,
	# 	bootlevel_names[level],
	# 	bootlevels[level].first_fn,
	# 	bootlevels[level].last_fn);

# ─────────────────────────────────────────────────────────────────────────────────────────────┐ │  
#   │ │                       --- Tracers                                                                                  │ │  
#   │ │                    /->-*-   Kernel Function Tracer                                                                 │ │  
#   │ │                  /-|--[ ]     Kernel Function Graph Tracer                                                         │ │  
#   │ │                  | |  [ ]   Interrupts-off Latency Tracer                                                          │ │  
#   │ │                  | |/-[*]   Scheduling Latency Tracer                                                              │ │  
#   │ │                  | || [ ]   Tracer to detect hardware latencies (like SMIs)                                        │ │  
#   │ │                  | || [*]   Trace syscalls                                                                         │ │  
#   │ │                  | |\>-*-   Create a snapshot trace buffer                                                         │ │  
#   │ │                  | |  [ ]     Allow snapshot to swap per CPU                                                       │ │  
#   │ │                  | |        Branch Profiling (No branch profiling)  --->                                           │ │  
#   │ │                  | \--[*]   Trace max stack                                                                        │ │  
#   │ │                  |    [*]   Support for tracing block IO actions                                                   │ │  
#   │ │                  |    [*]   Enable kprobes-based dynamic events                                                    │ │  
#   │ │                   \-->[*]   Enable uprobes-based dynamic events                                                    │ │  
#   │ │                       [*]   enable/disable function tracing dynamically                                            │ │  
#   │ │                       [*]   Kernel function profiler                                                               │ │  
#   │ │                       [ ]   Perform a startup test on ftrace                                                       │ │  
#   │ │                       [*]   Memory mapped IO tracing                                                               │ │  
#   │ │                       [ ]   Histogram triggers                                                                     │ │  
#   │ │                       < >   Test module for mmiotrace                                                              │ │  
#   │ │                       [ ]   Add tracepoint that benchmarks tracepoints                                             │ │  
#   │ │                       < >   Ring buffer benchmark stress tester                                                    │ │  
#   │ │                       [ ]   Ring buffer startup self test                                                          │ │  
#   │ │                       [ ]   Show eval mappings for trace events                                                    │ │  
#   │ │                       [*]   Trace gpio events                                                                      │ │  
#   │ │                                                          




				# ftrace: vearly 10 entries, ftrace_notrace=2776, ftrace_filter=1248
	
# [    0.000000] ftrace: vearly 10 entries, ftrace_notrace=2802, ftrace_filter=1248
# [    0.000000] ftrace: allocating 36956 entries in 145 pages
# [    0.000000] Starting tracer 'function'
# [    0.000000] tsc: Fast TSC calibration using PIT
# [    0.004000] Hierarchical RCU 



# [    0.363601]   <idle>-0       0dp.. 55725us : boot_cpu_state_init <-start_kernel
# [    0.364244]   <idle>-0       0dp.. 55725us : kvm_guest_cpu_init <-kvm_smp_prepare_boot_cpu
# [    0.364881]   <idle>-0       0dp.. 55743us : kvm_spinlock_init <-kvm_smp_prepare_boot_cpu
# [    0.365432]   <idle>-0       0dp.. 55744us : build_all_zonelists_init <-build_all_zonelists
# [    0.365991]   <idle>-0       0dp.. 55751us : page_alloc_init <-start_kernel
# [    0.366442]   <idle>-0       0dp.. 59044us : pidhash_init <-start_kernel
# [    0.366887]   <idle>-0       0dp.. 59054us : trap_init <-start_kernel
# [    0.367310]   <idle>-0       0dp.. 59071us : kvm_apf_trap_init <-trap_init
# [    0.367902]   <idle>-0       0dp.. 59072us : mem_init <-start_kernel
# [    0.368458]   <idle>-0       0dp.. 59076us : gart_iommu_hole_init <-pci_iommu_alloc


## bootlevel enabled
## initcall=selinux_init+0x0/0x174
## initcall=smack_init+0x0/0x204
## initcall=tomoyo_init+0x0/0x5b
## initcall=apparmor_init+0x0/0x2c8
## initcall=integrity_iintcache_init+0x0/0x2e

# 0,console, 	first=con_init,					last=univ8250_console_init
# 1,security, 	first=selinux_init,				last=integrity_iintcache_init
# 2,early, 		first=trace_init_flags_sys_exit,last=initialize_ptr_random
# 3,pure, 		first=ipc_ns_init,				last=net_ns_init
# 4,core, 		first=xen_pvh_gnttab_setup,		last=__gnttab_init
# 5,postcore, 	first=irq_sysfs_init,			last=kobject_uevent_init
# 6,arch, 		first=bts_init,					last=pci_arch_init
# 7,subsys, 	first=init_vdso,				last=watchdog_init
# 8,fs, 		first=nmi_warning_debugfs,		last=acpi_reserve_resources
# 9,rootfs, 	first=populate_rootfs,			last=ir_dev_scope_init
# 10,device, 	first=ia32_binfmt_init,			last=mcheck_init_device
# 11,late, 		first=tboot_late_init,			last=regulator_init_complete
