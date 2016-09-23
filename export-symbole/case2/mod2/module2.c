#include <linux/module.h>
#include <linux/kernel.h>

int hello_start(void)
{
	printk(KERN_INFO "Loading module2 module ...\n");

        return 0;
}

void hello_end(void)
{
        printk(KERN_INFO "Unloading module2 ...\n");
}

void m2_func(void)
{
        printk(KERN_INFO "This a function in module2\n");
}

module_init(hello_start);
module_exit(hello_end);

MODULE_LICENSE("GPL");
EXPORT_SYMBOL(m2_func);
