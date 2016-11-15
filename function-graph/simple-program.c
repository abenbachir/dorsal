#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>	

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)


void merge(long int *arr, int size1, int size2) 
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

void mergeSort(long int *arr, int size) {
    if (size == 1)
        return;  

    int size1 = size/2, size2 = size-size1;
    mergeSort(arr, size1);
    mergeSort(arr+size1, size2);
    merge(arr, size1, size2);
}

int initializeArray(char* filename, long int** array_output)
{
	
	char *fcontent = NULL;
	FILE *fp = fopen(filename, "r");
	fseek(fp, 0, SEEK_END); 
	int fsize = ftell(fp);
	fseek(fp, 0, SEEK_SET); 
	fcontent = malloc(fsize);
	fread(fcontent, 1, fsize, fp);

	// count ',' occurrence
	char* str = fcontent;
	int i;
	for (i=0; fcontent[i]; fcontent[i]==',' ? i++ : *fcontent++);
	int array_size = i+1;
	*array_output = malloc(array_size * sizeof(long int*)); 
	
	const char s[2] = ",";
    char *token;
    i = 0;
    // get the first token
	token = strtok(str, s);
	long int* array = *array_output;
	while( token != NULL ) 
	{
		// printf( " %s\n", token );
		// printf( "atoi %d\n", atoi(token) );
		// printf( "strtoul %d\n", strtoul(token, NULL, 10) );
		array[i++] =  atoi(token);
		// printf( "%d\n", array[i-1] );
		token = strtok(NULL, s);		
	}

    return array_size;
}

void main()
{
	struct timespec ts_start, ts_end;
	long int* array = NULL;
	int size = initializeArray("input.txt", &array);
	// printf("size=%d\n", size );

    // Start merge sort
    tic(ts_start);
    mergeSort(array, size);
    toc(ts_end);
    unsigned long int nanoseconds = elapsed_nsec(ts_start, ts_end);

    printf("%lu\n", nanoseconds);
    free(array);
}
