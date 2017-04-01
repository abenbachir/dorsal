/*
 ============================================================================
 Name        : MergeSort_multiThreaded.c
 Author      : Ashraf Saleh
 Version     :
 Copyright   : refer to my blog www.codingrush.wordpress.com
 Description : The ordinary merge sort (nlog(n)) using multi threads
 	 	 	   the objective of this assignment to create, use posix threads
 	 	 	   and not to improve complexity.
 	 	 	   see Introduction to algorithms (CORMEN) for advanced multi threaded
 	 	 	   merge sort
 ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
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

void* merge_sort(void* param){
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

int main(void) {
    char* filename= "input.txt";
	if(reader(filename)){
        printf("File not found %s\n", filename);
        return 0;
    }
	b = (int*)malloc(sizeof(int)*n);
	struct index start;
	start.p = 0;    start.r = n-1;
	pthread_t start_thread;

	struct timeval tv;
	gettimeofday(&tv,NULL);
	long long t1 = tv.tv_usec;

	pthread_create(&start_thread,NULL,merge_sort,&start);
	pthread_join(start_thread,NULL);

	gettimeofday(&tv,NULL);
	long long t2 = tv.tv_usec;

	printf("elapsed time = %lld usec\n",t2-t1);
	print(a);
	writer("sorted.txt");
	return 0;
}
