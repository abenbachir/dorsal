#include <iostream>
#include <sys/time.h>
#include <time.h>
using namespace std;

#define SIZE 128
#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)


void write_func(int* buffer, int value)
{
	buffer[value] = value;
}

void benchmark_normal() {
    int i, j;    
    int data[SIZE][SIZE]; 
    // original version
    for(i = 0; i < 128; i++)
        for(j = 0; j < 128; j++)
            data[i][j] = 0;
}

void benchmark_pagefault() {
    int i, j;
    int data[SIZE][SIZE]; 
    // new version
    for(j = 0; j < 128; j++)
        for(i = 0; i < 128; i++)
            data[i][j] = i;
}

int main()
{
    int size = 1000;
    int* buffer = new int[size];
    
    struct timespec ts_start, ts_end;
    cout << "time,type" << endl; 
    // for(int i = 0; i < 100; i++)
    // {
    // 	tic(ts_start);
    // 	benchmark_normal();
    //     toc(ts_end);

    // 	cout << elapsed_nsec(ts_start, ts_end) << ",normal"<<endl;
    // }

    for(int i = 0; i < 100; i++)
    {
        tic(ts_start);
        benchmark_pagefault();
        toc(ts_end);

        cout << elapsed_nsec(ts_start, ts_end) << ",page_faults"<<endl;
    }
    
    delete buffer;
    return 0;
}
