#include <linux/time.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/qemu-hypertrace.h>


/* Return 1 if the difference is negative, otherwise 0.  */
int timeval_subtract(struct timeval *result, struct timeval *t2, struct timeval *t1)
{
    long int diff = (t2->tv_usec + 1000000 * t2->tv_sec) - (t1->tv_usec + 1000000 * t1->tv_sec);
    result->tv_sec = diff / 1000000;
    result->tv_usec = diff % 1000000;

    return (diff<0);
}


////////////// ///////////////
int __init my_hypertrace_init(void)
{
	uint repeat = 1E6;
	struct timeval tvBegin, tvEnd, tvDiff;
    printk(KERN_INFO "my_hypertrace_benchmark:loading kernel module ... \n");

    printk(KERN_INFO "Max clients : %llu \n", qemu_hypertrace_max_clients());
    printk(KERN_INFO "Number of args : %llu \n", qemu_hypertrace_num_args());

	printk("Start benchmark \n");

    /* Set additional event arguments */
    uint64_t client  = 0;
    uint64_t *data = qemu_hypertrace_data(client);
	// begin
    do_gettimeofday(&tvBegin);
    uint i = 0;
    for ( ; i < repeat; i++) {
        data[0] = i;
        qemu_hypertrace(client, 0xfeca);
    }
 	//end
    do_gettimeofday(&tvEnd);
    timeval_subtract(&tvDiff, &tvEnd, &tvBegin);
    uint ns = timeval_to_ns(&tvDiff);
    printk(KERN_INFO "elapsed : %lu ns \n", ns);
    printk(KERN_INFO "event cost : %lu ns \n", ns/repeat);
    printk(KERN_INFO "event freq : %lu ns \n", 1000 * 1 / (ns / repeat));
    return 0;
}

void __exit my_hypertrace_cleanup(void)
{
    printk(KERN_INFO "my_hypertrace:unloading kernel module\n");
}

module_init(my_hypertrace_init);
module_exit(my_hypertrace_cleanup);

MODULE_DESCRIPTION("Simple benchmark of emitting hypertrace to QEMU's hypertrace device");
MODULE_AUTHOR("Abder Benbachir");
MODULE_LICENSE("GPL");
