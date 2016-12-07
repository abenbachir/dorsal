#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>	
#include <unistd.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)

static long int array[] = { 7, 6, 57, 83, 79, 80, 47, 78, 82, 65, 80, 59, 0, 44, 22, 88, 23, 97, 65, 
	78, 86, 37, 8, 5, 16, 10, 13, 64, 98, 61, 48, 58, 19, 5, 93, 99, 37, 40, 29, 20, 5, 61, 31, 58, 5,
	5, 98, 29, 2, 63 };

void merge(long int *arr, int size1, int size2) 
{
	sleep(0.5);
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
    __asm__("nop");	
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
/*    srand((unsigned) time(NULL));
	// fill the array with values
    for (int i = 0; i < 50; i++) {
        printf("%lu,",  rand() % 100);
    }
	return;*/
	struct timespec ts_start, ts_end;
	// printf("#...\nelapsed_time\n");
	// read fomr file
	// long int* array = NULL;
	// int size = initializeArray("input-50.txt", &array);
	// printf("size=%d\n", size );
	int size = 50;

 //    for (int i = 0; i<1000; i++)
 //    {
	//     tic(ts_start);
	//     mergeSort(array, size);
	//     toc(ts_end);
	//     unsigned long int nanoseconds = elapsed_nsec(ts_start, ts_end);
	//     printf("%lu\n", nanoseconds);
	// }
	mergeSort(array, size);
    // free space
    // free(array);

}
