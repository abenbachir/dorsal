// see http://stackoverflow.com/questions/5400275/fast-large-width-non-cryptographic-string-hashing-in-python
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

static inline long string_hash(char* string, int length)
{
	int len = length;
    unsigned char *p;
    long x;      /* Notice the 64-bit hash, at least on a 64-bit system */

    p = (unsigned char *) string;
    x = *p << 7;
    while (--len >= 0){
        x = (1000003*x) ^ *p++;
    }
    x ^= length;
    if (x == -1)
        x = -2;
    return x;
}

int main()
{	
	struct timespec start, end;
	char* buffer = "intel_uncore_forcewake_domain_to_str.13448aso;isdkjhvasdgsdjlgufsdlkuh";
	int length = 77;

	long benchmarks = 0;
	int limit = 1E7;
	for(int i = 0; i < limit; i++)
	{
		tic(start);
		long result = string_hash(buffer, length);
		toc(end);

		unsigned long int ns = elapsed_nsec(start, end);
		benchmarks += ns;
	    // printf("%lu ns\n", ns);
	}
	printf("mean = %f ns\n", (double) benchmarks/limit);
	return 0;
}