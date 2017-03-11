#include <iostream>
#include <sys/time.h>
#include <time.h>
using namespace std;


#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

void write_func(int* buffer, int value)
{
	buffer[value] = value;
}

int main()
{
    int size = 1000;
    int* buffer = new int[size];
    struct timespec ts_start, ts_end;

    for(int i = 0; i < size; i++)
    {
    	// tic(ts_start);
    	// buffer[i] = i;
    	write_func(buffer, i);
    	// toc(ts_end);

    	// cout << i << ","<< elapsed_nsec(ts_start, ts_end) << endl;
    }
    
    delete buffer;
    return 0;
}
