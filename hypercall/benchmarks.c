#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>
#include <stddef.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

#define do_hypercall(nr, p1, p2, p3, p4) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(nr), "b"(p1), "c"(p2), "d"(p3), "S"(p4))


#define do_hypercall_0() __asm__ __volatile__(".byte 0x0F,0x01,0xC1\n":: )


void my_hypercall(void) 
{
	do_hypercall(99, 100, 101, 102, 103);
}

void benchmark(int repeat)
{
    struct timespec ts_start, ts_end;
    ulong i = 0;

    for ( i=0; i < repeat; i++) {
        tic(ts_start);
        do_hypercall(99, 100, 101, 102, 103);
        toc(ts_end);
        unsigned long int ns = elapsed_nsec(ts_start, ts_end);
        // printf("%lu\n", ns);
        // sleep(1);
    }
}

enum kvm_reg {
    VCPU_REGS_RAX = 0,
    VCPU_REGS_RCX = 1,
    VCPU_REGS_RDX = 2,
    VCPU_REGS_RBX = 3,
    VCPU_REGS_RSP = 4,
    VCPU_REGS_RBP = 5,
    VCPU_REGS_RSI = 6,
    VCPU_REGS_RDI = 7,
    VCPU_REGS_R8 = 8,
    VCPU_REGS_R9 = 9,
    VCPU_REGS_R10 = 10,
    VCPU_REGS_R11 = 11,
    VCPU_REGS_R12 = 12,
    VCPU_REGS_R13 = 13,
    VCPU_REGS_R14 = 14,
    VCPU_REGS_R15 = 15,
    VCPU_REGS_RIP,
    NR_VCPU_REGS
};

struct kvm_vcpu_arch {
    /*
     * rip and regs accesses must go through
     * kvm_{register,rip}_{read,write} functions.
     */
    unsigned long regs[NR_VCPU_REGS];

};
        // "mov %c[rbp](%0), %%rbp \n\t" 
#define load_register(vcpu) asm(\
        "mov $0x111, %%rax \n\t" \
        "mov %c[rax](%0), %%rax \n\t" \
        "mov %c[rbx](%0), %%rbx \n\t" \
        "mov %c[rdx](%0), %%rdx \n\t" \
        "mov %c[rsi](%0), %%rsi \n\t" \
        "mov %c[rdi](%0), %%rdi \n\t" \
        "mov %c[r8](%0),  %%r8  \n\t" \
        "mov %c[r9](%0),  %%r9  \n\t" \
        "mov %c[r10](%0), %%r10 \n\t" \
        "mov %c[r11](%0), %%r11 \n\t" \
        "mov %c[r12](%0), %%r12 \n\t" \
        "mov %c[r13](%0), %%r13 \n\t" \
        "mov %c[r14](%0), %%r14 \n\t" \
        "mov %c[r15](%0), %%r15 \n\t" \
          : : "c"(&vcpu), \
        [rax]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RAX])), \
        [rbx]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RBX])), \
        [rcx]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RCX])), \
        [rdx]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RDX])), \
        [rsi]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RSI])), \
        [rdi]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RDI])), \
        [rbp]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RBP])), \
        [r8]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R8])), \
        [r9]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R9])), \
        [r10]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R10])), \
        [r11]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R11])), \
        [r12]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R12])), \
        [r13]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R13])), \
        [r14]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R14])), \
        [r15]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R15])) \
        : "cc", "memory",  \
        "rax", "rbx", "rdi", "rsi", \
        "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15" \
    )
#define store_registers(vcpu) asm(\
        "mov $0x111, %%rax \n\t" \
        "mov %%r8,  %c[r8](%0) \n\t" \
        "mov %%r9,  %c[r9](%0) \n\t" \
        "mov %%r10, %c[r10](%0) \n\t" \
        "mov %%r11, %c[r11](%0) \n\t" \
        "mov %%r12, %c[r12](%0) \n\t" \
        "mov %%r13, %c[r13](%0) \n\t" \
        "mov %%r14, %c[r14](%0) \n\t" \
        "mov %%r15, %c[r15](%0) \n\t" \
          : : "c"(&vcpu), \
        [rax]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RAX])), \
        [rbx]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RBX])), \
        [rcx]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RCX])), \
        [rdx]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RDX])), \
        [rsi]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RSI])), \
        [rdi]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RDI])), \
        [rbp]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_RBP])), \
        [r8]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R8])), \
        [r9]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R9])), \
        [r10]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R10])), \
        [r11]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R11])), \
        [r12]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R12])), \
        [r13]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R13])), \
        [r14]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R14])), \
        [r15]"i"(offsetof(struct kvm_vcpu_arch, regs[VCPU_REGS_R15])) \
        : "cc", "memory",  \
        "rax", "rbx", "rdi", "rsi", \
        "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15" \
    )
int main(int argc, char** argv)
{
/*    struct timespec ts_start, ts_end;
    unsigned long int ns;
    struct kvm_vcpu_arch vcpu;
    for (int i=0; i < NR_VCPU_REGS; i++) {
        vcpu.regs[i] = 0;
    }
    tic(ts_start);
    int repeat = 1E9;
    for (int i=0; i < repeat; i++) {
        load_register(vcpu);
        store_registers(vcpu);
    }
    toc(ts_end);
    ns = elapsed_nsec(ts_start, ts_end);
    printf("%lf\n", (double)ns/repeat);

    for (int i=0; i < NR_VCPU_REGS; i++) {
        printf("%d -> %d\n", i, vcpu.regs[i]);
    }
    */
	 do_hypercall(99, 100, 101, 102, 103);
    return 0;
}
