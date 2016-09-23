#include <linux/module.h>
#include <linux/kernel.h>

int hello_start(void)
{
	printk(KERN_INFO "Loading m2 module ...\n");

        return 0;
}

void hello_end(void)
{
        printk(KERN_INFO "Unloading m2 ...\n");
}

void func_m2(void)
{
        printk(KERN_INFO "This a function in m2\n");
}

module_init(hello_start);
module_exit(hello_end);

MODULE_LICENSE("GPL");
EXPORT_SYMBOL(func_m2);
