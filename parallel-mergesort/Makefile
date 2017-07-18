all:
#	gcc -finstrument-functions -pthread main.c -o mergesort
	gcc main.c -o mergesort -pthread -finstrument-functions -llttng-ust -ldl
clean:
	rm mergesort
