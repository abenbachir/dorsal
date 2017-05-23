#!/usr/bin/env Rscript
library(ggplot2)
mydata=as.vector(read.table("./hypercall/hypercalls.dat", header=TRUE, skip=1))

#mydat = remove_outliers(mydata) 
# hist(mydata$Cost, 
#      main = paste("Hypercall Overhead - No hypercall handling in host-side"),
#      xlab="Overhead in nanoseconds",
#      xlim=c(250,400),
#      breaks=100000000)

#plot(h, breaks=300,xlim=c(300,600))
#d = density(mydata) # returns the density data 
#plot(d, ,xlim=c(0,10000)) # plots the results


qplot <- ggplot(mydata, aes(Cost)) +
  geom_density(adjust = 1/4, position = "identity") +
  theme_bw()

plot(qplot)