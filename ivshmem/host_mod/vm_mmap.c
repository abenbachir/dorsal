#include <linux/version.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/skbuff.h>
#include <linux/un.h>
#include <linux/proc_fs.h>

#include <linux/mm.h>
#include <linux/mman.h>
#include <linux/fs.h>
#include <linux/file.h>
#include <asm/segment.h>
#include <asm/uaccess.h>

struct file *file_open(const char *path, int flags, int rights) 
{
    struct file *filp = NULL;
    mm_segment_t oldfs;
    int err = 0;

    oldfs = get_fs();
    set_fs(get_ds());
    filp = filp_open(path, flags, rights);
    set_fs(oldfs);
    if (IS_ERR(filp)) {
        err = PTR_ERR(filp);
        return NULL;
    }
    return filp;
}

void file_close(struct file *file) 
{
    filp_close(file, NULL);
}

int file_read(struct file *file, unsigned long long offset,
	unsigned char *data, unsigned int size) 
{
    mm_segment_t oldfs;
    int ret;

    oldfs = get_fs();
    set_fs(get_ds());

    ret = kernel_read(file, data, size, &offset);

    set_fs(oldfs);
    return ret;
}

static void* my_page;

static int ops_map(struct file *filp, struct vm_area_struct *vma)
{
	printk(KERN_INFO "mod: ops_map.\n");

	vma->vm_pgoff = (unsigned long)my_page >> PAGE_SHIFT;
	struct page *page = vmalloc_to_page((void *)my_page);

	unsigned long pfn = page_to_pfn(page);
	return remap_pfn_range(vma, vma->vm_start, pfn, PAGE_SHIFT, vma->vm_page_prot);

	// if (io_remap_pfn_range(vma, vma->vm_start, vma->vm_pgoff,
 //           			vma->vm_end - vma->vm_start, vma->vm_page_prot))
	// 	return -EAGAIN;
 //    return 0;
}


static struct file_operations fops = {
	.mmap = ops_map,
};

struct mmap_info {
	char data[PAGE_SIZE];
};
/*
 * module init/exit
 */
static int __init mod_init(void)
{
	int ret;
	char data[PAGE_SIZE];
	unsigned long *map;
	char *path = "/tmp/test.txt";
	my_page = vmalloc(PAGE_SIZE);
	const struct file_operations *old_fops;

	printk(KERN_INFO "mod init.\n");
	struct file *filp = file_open(path, O_RDWR, 0);
	if (filp == NULL) {
		printk(KERN_INFO "mod: %s not found.\n",path);
		return -1;
	}
	
	// read first page from the file
	file_read(filp, 0,data, PAGE_SIZE);
	printk(KERN_INFO "data=%s\n", data);

	/* mmap file into kernel memory */
	// old_fops = filp->f_op;
	// filp->f_op = &fops;
	map = (unsigned long*)vm_mmap(filp, 0, PAGE_SIZE, PROT_READ|PROT_WRITE, MAP_SHARED, 0);
	
	if (IS_ERR(map)) {
		printk(KERN_INFO"vm_mmap error\n");
		return -1;
	}

	// filp->f_op = (typeof(filp->f_op))old_fops;
	printk(KERN_INFO "map = %lu \n", map);

	/* Kernel Oops */
	printk(KERN_INFO "map* = %s \n", *(unsigned long*)map);

	file_close(filp);
	return 0;
}

static void __exit mod_cleanup(void)
{
	if (my_page)
		vfree(my_page);

	printk(KERN_INFO "mod: removing module.\n");
}

module_init(mod_init);
module_exit(mod_cleanup);

MODULE_LICENSE("GPL and additional rights");
MODULE_AUTHOR("");
MODULE_DESCRIPTION("mod");
MODULE_VERSION("1.0");

/*
KENRL Oops output :

[   81.944785] mod: ops_map.
[   81.944786] map = 140689784000512 
[  240.598359] mod: removing module.
[  250.406455] mod init.
[  250.406459] data=123456789...

[  250.406461] map = 140391302139904 
[  250.406463] BUG: unable to handle kernel paging request at 00007faf65b19000
[  250.406913] IP: mod_init+0xe1/0x1000 [vm_mmap]
[  250.407161] PGD 1367cc067 P4D 1367cc067 PUD 135068067 PMD 135069067 PTE 0
[  250.407535] Oops: 0000 [#1] SMP
[  250.407713] Modules linked in: vm_mmap(OE+) snd_hda_codec_generic snd_hda_intel snd_hda_codec snd_hwdep ppdev snd_hda_core snd_pcm snd_timer snd input_leds joydev serio_raw i2c_piix4 soundcore parport_pc ib_iser parport qemu_fw_cfg rdma_cm configfs mac_hid iw_cm ib_cm ib_core iscsi_tcp libiscsi_tcp libiscsi scsi_transport_iscsi ip_tables x_tables autofs4 btrfs zstd_decompress zstd_compress xxhash raid10 raid456 libcrc32c async_raid6_recov async_memcpy async_pq async_xor async_tx xor raid6_pq raid1 raid0 multipath linear crct10dif_pclmul crc32_pclmul ghash_clmulni_intel pcbc qxl drm_kms_helper syscopyarea sysfillrect sysimgblt fb_sys_fops ttm drm psmouse aesni_intel aes_x86_64 crypto_simd cryptd glue_helper virtio_blk virtio_net pata_acpi floppy [last unloaded: vm_mmap]
[  250.411461] CPU: 0 PID: 2450 Comm: insmod Tainted: G           OE   4.14.0-rc4+ #55
[  250.411880] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.10.1-1ubuntu1 04/01/2014
[  250.412367] task: ffff8a8fb679b000 task.stack: ffffa0658101c000
[  250.412692] RIP: 0010:mod_init+0xe1/0x1000 [vm_mmap]
[  250.413030] RSP: 0018:ffffa0658101ec78 EFLAGS: 00010286
[  250.413337] RAX: 0000000000000016 RBX: ffff8a8fb6ccb600 RCX: 0000000000000006
[  250.413963] RDX: 0000000000000000 RSI: 0000000000000082 RDI: ffff8a8fbcc0dc90
[  250.414563] RBP: ffffa0658101fc90 R08: 0000000000000001 R09: 0000000000000238
[  250.415224] R10: 0000000000000000 R11: 0000000000000238 R12: 00007faf65b19000
[  250.415804] R13: 0000000000000000 R14: ffffa0658101fea0 R15: ffff8a8fae0fe360
[  250.416473] FS:  00007faf65b0d700(0000) GS:ffff8a8fbcc00000(0000) knlGS:0000000000000000
[  250.417003] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
[  250.417333] CR2: 00007faf65b19000 CR3: 0000000136755001 CR4: 00000000003606f0
[  250.417797] DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
[  250.418284] DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
[  250.418750] Call Trace:
[  250.418926]  ? radix_tree_lookup_slot+0x22/0x50
[  250.419234]  ? find_get_entry+0x1e/0xc0
[  250.419483]  ? __find_get_block+0xb5/0x2b0
[  250.419895]  ? __find_get_block+0xb5/0x2b0
[  250.420220]  ? __update_load_avg_se.isra.37+0x14a/0x150
[  250.420529]  ? __update_load_avg_se.isra.37+0x14a/0x150
[  250.420859]  ? update_load_avg+0x417/0x580
[  250.421107]  ? update_curr+0x78/0x1c0
[  250.421363]  ? __enqueue_entity+0x5c/0x60
[  250.421601]  ? enqueue_entity+0x113/0x770
[  250.421835]  ? check_preempt_wakeup+0x192/0x260
[  250.422154]  ? check_preempt_curr+0x82/0x90
[  250.422460]  ? ttwu_do_wakeup+0x1e/0x140
[  250.422757]  ? ttwu_do_activate+0x7a/0x90
[  250.423099]  ? try_to_wake_up+0x59/0x490
[  250.423429]  ? default_wake_function+0x12/0x20
[  250.423764]  ? __wake_up_common+0x87/0x140
[  250.424070]  ? ep_poll_callback+0x130/0x2e0
[  250.424671]  ? update_load_avg+0x417/0x580
[  250.425405]  ? update_load_avg+0x417/0x580
[  250.425990]  ? set_next_entity+0xcb/0x1e0
[  250.426557]  ? pick_next_task_fair+0x332/0x580
[  250.427142]  ? __slab_free+0xc8/0x300
[  250.427680]  ? __schedule+0x3cf/0x830
[  250.428214]  ? 0xffffffffc0197000
[  250.429053]  do_one_initcall+0x52/0x1a0
[  250.429725]  ? __vunmap+0x81/0xb0
[  250.430233]  ? kfree+0x14a/0x160
[  250.430838]  ? kmem_cache_alloc_trace+0xe3/0x1a0
[  250.431380]  do_init_module+0x5f/0x209
[  250.431854]  load_module+0x2951/0x2d20
[  250.432346]  ? ima_post_read_file+0x7e/0xa0
[  250.432867]  SYSC_finit_module+0xe5/0x120
[  250.433384]  ? SYSC_finit_module+0xe5/0x120
[  250.433842]  SyS_finit_module+0xe/0x10
[  250.434275]  entry_SYSCALL_64_fastpath+0x1e/0xa9
[  250.434753] RIP: 0033:0x7faf656339f9
[  250.435173] RSP: 002b:00007ffe36eb9f48 EFLAGS: 00000246 ORIG_RAX: 0000000000000139
[  250.435886] RAX: ffffffffffffffda RBX: 0000556caa0a91e0 RCX: 00007faf656339f9
[  250.436501] RDX: 0000000000000000 RSI: 0000556ca7f6af8b RDI: 0000000000000003
[  250.437202] RBP: 00007faf658f2b00 R08: 0000000000000000 R09: 00007faf658f4ea0
[  250.437887] R10: 0000000000000003 R11: 0000000000000246 R12: 00007faf658f2b58
[  250.438577] R13: 00007ffe36eba908 R14: 0000000000002710 R15: 0000000000001010
[  250.439363] Code: 48 3d 00 f0 ff ff 49 89 c4 76 11 48 c7 c7 70 90 64 c0 e8 44 8d 54 ec 83 c8 ff eb 2b 48 89 c6 48 c7 c7 81 90 64 c0 e8 30 8d 54 ec <49> 8b 34 24 48 c7 c7 8f 90 64 c0 e8 20 8d 54 ec 31 f6 48 89 df 
[  250.441340] RIP: mod_init+0xe1/0x1000 [vm_mmap] RSP: ffffa0658101ec78
[  250.441947] CR2: 00007faf65b19000
[  250.442429] ---[ end trace 2f8f4fe63f807c43 ]---

*/