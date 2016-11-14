#include <stdio.h>
#include <time.h>

#define HYPERCALL_NR 101
#define FUNC_ENTER (0)
#define FUNC_EXIT  (1)
#define do_hypercall(hypercall_nr, arg1, arg2, arg3) \
__asm__ __volatile__(".byte 0x0F,0x01,0xC1\n"::"a"(hypercall_nr), \
	"b"(arg1), \
	"c"(arg2), \
	"d"(arg3))

static long unsigned int func_count = 0;

void __attribute__ ((constructor)) trace_begin (void)
{
}
 
void __attribute__ ((destructor)) trace_end (void)
{
	// printf("%lu\n", func_count);
}

void __cyg_profile_func_enter (void *func,  void *caller)
{
#ifdef DO_HYPERCALL
	do_hypercall(HYPERCALL_NR, (unsigned long)func, (unsigned long)caller, FUNC_ENTER);
	func_count++;
#endif
}
 
void __cyg_profile_func_exit (void *func, void *caller)
{	
#ifdef DO_HYPERCALL
	do_hypercall(HYPERCALL_NR, (unsigned long)func, (unsigned long)caller, FUNC_EXIT);
	func_count++;
#endif
}


