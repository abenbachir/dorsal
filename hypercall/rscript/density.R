#!/usr/bin/env Rscript
library(ggplot2)
mydata=as.vector(read.table("./hypercall/hypercalls.dat", header=TRUE, skip=1))

sd <- sd(mydata$Cost)
mean <- mean(mydata$Cost)
median <- median(mydata$Cost)

qplot <- ggplot(mydata, aes(Cost)) +
  geom_density(adjust = 1) +
  labs(x ="Nanoseconds", y ="Density") +
  xlim(300, 375) +
  theme_bw()
plot(qplot)