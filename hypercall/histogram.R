#!/usr/bin/env Rscript

mydata=as.vector(read.table("./hypercall/test.dat", header=TRUE, skip=1)$Cost)
#mydata=as.vector(read.table("./hypercall/hypercall-with-trace-enabled.dat", header=TRUE, skip=1)$Cost)

#mydat = remove_outliers(mydata) 
hist(mydata, 
     main = paste("Hypercall Overhead - No hypercall handling in host-side"),
     xlab="Overhead in nanoseconds",
     xlim=c(300,500),
     breaks=1000000)

#plot(h, breaks=300,xlim=c(300,600))
#d = density(mydata) # returns the density data 
#plot(d, ,xlim=c(0,10000)) # plots the results