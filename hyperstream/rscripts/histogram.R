#!/usr/bin/env Rscript
library(ggplot2)

data_100MB = read.table("./hyperstream/data/hyperstream-file_100MB.dat", header=TRUE, skip=0)
data_10MB = read.table("./hyperstream/data/hyperstream-file_10MB.dat", header=TRUE, skip=0)
data_1MB = read.table("./hyperstream/data/hyperstream-file_1MB.dat", header=TRUE, skip=0)

data_100MB$size <- 100
data_10MB$size <- 10
data_1MB$size <- 1


data <- rbind(data_1MB, data_10MB, data_100MB)
data$size_type <- paste(as.character(data$size),'MB')
data$speed <- data$size*8/(data$elapsed_time / 10^9)

plot <- ggplot(data, aes(speed, fill=size_type, colour = size_type)) +
  geom_density(alpha = 0.1) +
  labs(title = "Hyperstream Transfer Speed Density") +
  labs(x="Transfer Speed Mbps") +
  labs(fill="File size", colour="File size") +
  theme_bw()

plot(plot)