#!/usr/bin/env Rscript
library(ggplot2)

mydata=read.table("./hyperstream/data/hyperstream-file_100MB.dat", header=TRUE, skip=0)

#mydat = remove_outliers(mydata) 

# convert to seconds
mydata$elapsed_time <- mydata$elapsed_time / 10^9

plot <- ggplot(mydata, aes(elapsed_time)) +
  geom_density() +
  labs(title = "Hyperstream density for 100 MB file") +
  labs(x="Transfer time (s)") +
  theme_bw()

plot(plot)