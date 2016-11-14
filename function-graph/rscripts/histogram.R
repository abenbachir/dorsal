#!/usr/bin/env Rscript
library(ggplot2)
# elapsed_time,func_calls
data_ins_hypercall = read.table("./function-graph/data/function-graph.dat", header=TRUE, sep = ',', skip=1)
data_ins = read.table("./function-graph/data/function-graph.dat", header=TRUE, sep = ',', skip=1)
data_noins = read.table("./function-graph/data/no-function-graph.dat", header=TRUE, sep = ',', skip=1)

# data$elapsed_time_us <- data$elapsed_time / 1000000
# data$ratio <- data$elapsed_time / data$func_calls

ins_density <- density(data_ins$elapsed_time) 
nosins_density <- density(data_noins$elapsed_time)

plot(nosins_density$y - ins_density$y)

# mydata <- data.frame(overhead = nosins_density$y - ins_density$y)
# plot <- ggplot(mydata, aes(overhead)) +
#   geom_density(alpha = 0.1) +
#   labs(title = "Hypercall function graph Density") +
#   labs(x="Elapsed time (us)") +
#   labs(fill="Number of entry & exit", colour="#Entry/Exit") +
#   theme_bw()
# plot(plot)

max_overhead <- 1 - max(data_noins$elapsed_time)/ max(data_ins$elapsed_time)
min_overhead <- 1 - min(data_noins$elapsed_time)/ min(data_ins$elapsed_time)
std_overhead <- 1 - sd(data_noins$elapsed_time)/ sd(data_ins$elapsed_time)
mean_overhead <- 1 - mean(data_noins$elapsed_time)/ mean(data_ins$elapsed_time)