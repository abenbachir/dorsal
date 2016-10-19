#!/usr/bin/env Rscript
library(lattice)

mydata = read.delim("./hypercall/hypercount.dat", sep=",")
x <- as.vector(mydata$duration)
y <- as.vector(mydata$hypercalls)

str(mydata)

xyplot <- xyplot(y~x, data=mydata, grid = TRUE, type = c("p", "r"))

plot(xyplot)