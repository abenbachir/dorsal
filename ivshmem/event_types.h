
#define COMM_SIZE 16
#define PAYLOAD_SIZE 80

#define KVM_ENTRY_EVENT_NR 20
#define KVM_EXIT_EVENT_NR 21
#define FUNC_TRACING_EVENT_NR 1000
#define SCHED_SWITCH_EVENT_NR 1001
#define SCHED_WAKING_EVENT_NR 1002
#define SCHED_WAKEUP_EVENT_NR 1003
#define SCHED_WAKEUP_NEW_EVENT_NR 1004
#define SCHED_PROCESS_FORK_EVENT_NR 1005
#define SCHED_PROCESS_FREE_EVENT_NR 1006
#define SCHED_PROCESS_EXIT_EVENT_NR 1007
#define SYS_ENTER_EVENT_NR 1100
#define SYS_EXIT_EVENT_NR 1101
#define SOFTIRQ_RAISE_EVENT_NR 1102
#define SOFTIRQ_ENTRY_EVENT_NR 1103
#define SOFTIRQ_EXIT_EVENT_NR 1104
#define IRQ_HANDLER_ENTRY_EVENT_NR 1105
#define IRQ_HANDLER_EXIT_EVENT_NR 1106
#define HRTIMER_INIT_EVENT_NR 1107
#define HRTIMER_START_EVENT_NR 1108
#define HRTIMER_EXPIRE_ENTRY_EVENT_NR 1109
#define HRTIMER_EXPIRE_EXIT_EVENT_NR 1110
#define HRTIMER_EXPIRE_CANCEL_EVENT_NR 1111

typedef signed char s8;
typedef unsigned char u8;

typedef signed short s16;
typedef unsigned short u16;

typedef signed int s32;
typedef unsigned int u32;

typedef signed long long s64;
typedef unsigned long long u64;

struct shm_config {
	// int can_write;
	unsigned long buff_size;
};

struct shm_event_entry {
	u16 cpu_id;
	u16 event_type;
	unsigned long long timestamp;
	char payload[PAYLOAD_SIZE];
};

/*
 * sched_switch
 */
struct sched_switch_payload {
	int prev_tid;
	int next_tid;
	int prev_prio;
	int next_prio;
	int prev_state;
	char prev_comm[COMM_SIZE];
	char next_comm[COMM_SIZE];
};

/*
 * sched_wakeup
 * sched_wakeup_new
 * sched_waking
 */
struct sched_wakeup_payload {
	int target_cpu;
	int prio;
	int tid;
	char comm[COMM_SIZE];
};

/*
 * sched_process_free
 * sched_process_exit
 */
struct sched_process_free_exit_payload {
	int tid;
	int prio;
	char comm[COMM_SIZE];
};
/*
 * sched_process_fork
 */
struct sched_process_fork_payload {
	unsigned int child_tid;
	unsigned int child_pid;
	unsigned int parent_tid;
	unsigned int parent_pid;
	char child_comm[COMM_SIZE];
	char parent_comm[COMM_SIZE];
};

/*
 * softirq_raise
 * softirq_entry
 * softirq_exit
 */
struct softirq_payload {

};

/*
 * irq_handler_entry
 * irq_handler_exit
 */
struct irq_handler_payload {
	int irq;
	int ret;
};

/*
 * hrtimer_init
 */
struct hrtimer_init_payload {
	u64 hrtimer;
	u64 clockid;
	u64 mode;
};

/*
 * hrtimer_start
 */
struct hrtimer_start_payload {
	u64 hrtimer;
	u64 function;
	u64 softexpires;
	u64 expires;
};

/*
 * hrtimer_expire_entry
 */
struct hrtimer_expire_entry_payload {
	u64 hrtimer;
	u64 function;
	u64 now;
};

/*
 * hrtimer_expire_exit
 */
struct hrtimer_expire_exit_payload {
	u64 hrtimer;
};

/*
 * hrtimer_cancel
 */
struct hrtimer_cancel_payload {
	u64 hrtimer;
};

struct sys_enter_payload {
	int syscall_nr;
};

struct sys_exit_payload {
	int syscall_nr;
	int ret;
};

struct kvm_entry_payload {
	unsigned int vcpu_id;
};

struct kvm_exit_payload {
	u32 isa;
	u64 guest_rip;
	unsigned int exit_reason;
};

void get_payload_from_num(int event_type, char *payload) {

}