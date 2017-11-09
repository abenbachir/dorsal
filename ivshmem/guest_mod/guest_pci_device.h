#include <linux/pci.h>

struct ivshmem_dev_t {
	/* (mmio) control registers i.e. the "register memory region" */
	void __iomem *regs_base_addr;
	resource_size_t regs_start;
	resource_size_t regs_len;
	/* data mmio region */
	void __iomem *data_base_addr;
	resource_size_t data_mmio_start;
	resource_size_t data_mmio_len;
	/* irq handling */
	unsigned int irq;
};


extern struct ivshmem_dev_t* get_ivshmem_dev(void);