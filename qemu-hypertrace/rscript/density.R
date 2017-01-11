#!/usr/bin/env Rscript
library(ggplot2)
data=as.vector(read.table("./qemu-hypertrace/data/hypertrace-disabled-cpu-scaling.dat", header=TRUE, skip=1))

sd <- sd(data$Cost)
mean <- mean(data$Cost)
median <- median(data$Cost)

qplot <- ggplot(data, aes(Cost)) +
  geom_density(adjust = 1) +
  labs(x ="Nanoseconds", y ="Density") +
  xlim(1950, 2100) +
  theme_bw()
plot(qplot)
