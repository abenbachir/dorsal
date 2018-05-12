#include <linux/module.h>
#include <linux/kernel.h>

extern void func_m2(void);

static int __init hello_start(void)
{
   printk(KERN_INFO "Loading m1 module ...\n");

   func_m2();

   return 0;
}

static void __exit hello_end(void)
{
   printk(KERN_INFO "Unloading m1 ...\n");
}

module_init(hello_start);
module_exit(hello_end);

MODULE_LICENSE("GPL");
