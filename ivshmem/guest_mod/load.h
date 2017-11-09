sudo dmesg -C
make
sudo rmmod guest_pci_device guest_shm_trace
echo "Loading..."
sudo insmod guest_pci_device.ko
sudo insmod guest_shm_trace.ko

dmesg | tail