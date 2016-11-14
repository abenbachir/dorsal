#include <stdio.h>
#include <stdlib.h>
#include <time.h>	

#define ARRAY_SIZE 10000
#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)


void merge(int *arr, int size1, int size2) 
{
    int temp[size1+size2];
    int ptr1=0, ptr2=0;

    while (ptr1+ptr2 < size1+size2) {
        if (ptr1 < size1 && arr[ptr1] <= arr[size1+ptr2] || ptr1 < size1 && ptr2 >= size2)
            temp[ptr1+ptr2] = arr[ptr1++];

        if (ptr2 < size2 && arr[size1+ptr2] < arr[ptr1] || ptr2 < size2 && ptr1 >= size1)
            temp[ptr1+ptr2] = arr[size1+ptr2++];
    }

    for (int i=0; i < size1+size2; i++)
        arr[i] = temp[i];
}

void mergeSort(int *arr, int size) {
    if (size == 1)
        return;  

    int size1 = size/2, size2 = size-size1;
    mergeSort(arr, size1);
    mergeSort(arr+size1, size2);
    merge(arr, size1, size2);
}


void main()
{
    struct timespec ts_start, ts_end;
	int array[ARRAY_SIZE];
    /* Intializes random number generator */
    srand((unsigned) time(NULL));
	// fill the array with values
    for (int i = 0; i < ARRAY_SIZE; i++) {
        array[i] = rand();
        printf("%lu,", array[i]);
    }

    // Start merge sort
    tic(ts_start);
    mergeSort(array, ARRAY_SIZE);
    toc(ts_end);
    unsigned long int nanoseconds = elapsed_nsec(ts_start, ts_end);

    printf("%lu\n", nanoseconds);
}

