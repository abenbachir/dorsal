mydata=as.vector(read.table("hypertrace.dat", header=TRUE, skip=1)$Cost)

hist(mydata, 
     main = paste("Histogram of Hypertrace Overhead"),
     xlim=c(1700,2600),
     breaks=1000000)

#d = density(mydata) # returns the density data 
#plot(d, ,xlim=c(0,10000)) # plots the results
