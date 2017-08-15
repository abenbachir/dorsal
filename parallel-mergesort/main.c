
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

#define tic(start) clock_gettime(CLOCK_MONOTONIC, &start)
#define toc(end) clock_gettime(CLOCK_MONOTONIC, &end)
#define elapsed_nsec(start, end) (end.tv_nsec + 1E9 * end.tv_sec) - (start.tv_nsec + 1E9 * start.tv_sec)


int* a;
int* b; //sorted array
int n;
int reader(char* filename){
	FILE* f = fopen(filename,"r");
	if(f == NULL)
        return -1;
    fscanf(f,"%d",&n);
	a = (int*) malloc(sizeof(int)*n);
	int i;
	for (i = 0; i < n; ++i)
		fscanf(f,"%d",&a[i]);
	fclose(f);
    return 0;
}

void print(int* a){
	int i;
	for (i = 0; i < n; ++i)
		printf("%d ",a[i]);
	printf("\n");
}

void writer(char* filename){
	FILE* f = fopen(filename,"w");
	fprintf(f,"sorted array of size %d :\n",n);
	int i;
	for (i = 0; i < n; ++i)
		fprintf(f,"%d ",b[i]);
	fprintf(f,"\n");
	fclose(f);
}

struct index{int p,r;};

void* merge_sort(void* param)
{
	struct index* pr = (struct index*) param;
	int p = pr->p,  r = pr->r , ret1,ret2;
	if (p==r)
		pthread_exit(0);

	pthread_t thread1,thread2;
	struct index pr1,pr2;
	int q = (p+r)/2;
	pr1.p = p;    pr1.r = q;
	pr2.p = q+1;  pr2.r = r;

	ret1 = pthread_create(&thread1,NULL,merge_sort,(void*) &pr1);
	if (ret1>0)
		printf("failed to create new thread 1\n");

	ret2 = pthread_create(&thread2,NULL,merge_sort,(void*) &pr2);
	if (ret2>0)
		printf("failed to create new thread 2\n");

	pthread_join(thread1,NULL);
	pthread_join(thread2,NULL);

	int k = p ,i = p ,j = q+1;

	while (i<=q && j<=r){
		if (a[i] < a[j])
			b[k++] = a[i++];
		else
			b[k++] = a[j++];
	}
	for (; i<=q ; i++)
		b[k++] = a[i];
	for (; j<=r ; j++)
		b[k++] = a[j];

	for (i= p ; i <= r ;i++)
		a[i] = b[i];

	pthread_exit(0);
	return NULL;
}

int main(void) 
{
	static struct timespec ts_start, ts_end;
	static struct timespec ts_start_sorting, ts_end_sorting;
	char* filename= "input.txt";
	unsigned long int sorting_time;
	// printf("total_time,sorting_time,sorting_overhead,io_overhead\n");
	tic(ts_start);

	if(reader(filename)){
		printf("File not found %s\n", filename);
		return 0;
	}

	b = (int*)malloc(sizeof(int)*n);
	struct index start;
	start.p = 0;
	start.r = n-1;
	pthread_t start_thread;
	
	tic(ts_start_sorting);
	pthread_create(&start_thread,NULL,merge_sort,&start);
	pthread_join(start_thread,NULL);
	toc(ts_end_sorting);
	sorting_time = elapsed_nsec(ts_start_sorting, ts_end_sorting);
	
	writer("sorted.txt");
	toc(ts_end);	
	unsigned long int total_time = elapsed_nsec(ts_start, ts_end);

	printf("%lu,%lu,%f,%f\n", total_time, sorting_time, (double)sorting_time/total_time, (double)(total_time-sorting_time)/total_time);
	return 0;
}
