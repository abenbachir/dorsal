/*
Remember: mmap, like most fops, does not work with debugfs as of 4.9! https://patchwork.kernel.org/patch/9252557/

Adapted from:
https://coherentmusings.wordpress.com/2014/06/10/implementing-mmap-for-transferring-data-from-user-space-to-kernel-space/
*/

#include <linux/uaccess.h> /* copy_from_user */
#include <linux/debugfs.h>
#include <linux/fs.h>
#include <linux/init.h>
#include <linux/kernel.h> /* min */
#include <linux/mm.h>
#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/slab.h>


#define PROC_VMSYNC_NAME "host_vmsync"
#define BUFFER_SIZE 4096

struct mmap_info {
	char *data;
};

struct mmap_info *mmap_info;



/* First page access. */
static int vm_fault(struct vm_fault *vmf)
{
	struct vm_area_struct *vma = vmf->vma;
	struct page *page;
	struct mmap_info *info;

	info = (struct mmap_info *)vma->vm_private_data;
	if (info->data) {
		page = virt_to_page(info->data);
		get_page(page);
		vmf->page = page;
	}
	return 0;
}

static struct vm_operations_struct vm_ops =
{
	.fault = vm_fault,
};

static int mmap(struct file *filp, struct vm_area_struct *vma)
{
	vma->vm_ops = &vm_ops;
	vma->vm_flags |= VM_DONTEXPAND | VM_DONTDUMP;
	vma->vm_private_data = filp->private_data;
	return 0;
}

static int open(struct inode *inode, struct file *filp)
{
	// pr_info("virt_to_phys = 0x%llx\n", (unsigned long long)virt_to_phys((void *)mmap_info));
	
	filp->private_data = mmap_info;
	return 0;
}

static int release(struct inode *inode, struct file *filp)
{
	filp->private_data = NULL;
	mmap_info->data[3]++;
	return 0;
}

static const struct file_operations fops = {
	.mmap = mmap,
	.open = open,
	.release = release,
};


static int myinit(void)
{
	mmap_info = kmalloc(sizeof(struct mmap_info), GFP_KERNEL);
	mmap_info->data = (char *)get_zeroed_page(GFP_KERNEL);
	memcpy(mmap_info->data, "1234\n", BUFFER_SIZE);
	proc_create(PROC_VMSYNC_NAME, 0, NULL, &fops);
	return 0;
}

static void myexit(void)
{
	free_page((unsigned long)mmap_info->data);
	kfree(mmap_info);
	remove_proc_entry(PROC_VMSYNC_NAME, NULL);
}

module_init(myinit)
module_exit(myexit)
MODULE_LICENSE("GPL");