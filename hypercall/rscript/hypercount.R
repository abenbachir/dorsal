#!/usr/bin/env Rscript
library(lattice)

mydata = read.delim("./hypercall/data/hypercount.dat", sep=",")
x <- as.vector(mydata$duration)
y <- as.vector(mydata$hypercalls)

str(mydata)

xyplot <- xyplot(y~x,
                 main="Number of hypercalls that we get during a period of time",
                 xlab = "Time duration (ns)",
                 ylab="Number of hypercalls",
                 data=mydata, 
                 grid = TRUE, 
                 type = c("p", "r")
)

plot(xyplot)