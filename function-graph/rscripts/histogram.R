#!/usr/bin/env Rscript
library(ggplot2)
# elapsed_time,func_calls
data_ins_hypercall = read.table("./function-graph/data/function-graph-dohypercall.dat", header=TRUE, sep = ',', skip=1)
data_ins = read.table("./function-graph/data/function-graph.dat", header=TRUE, sep = ',', skip=1)
data_noins = read.table("./function-graph/data/no-function-graph.dat", header=TRUE, sep = ',', skip=1)

# data$elapsed_time_us <- data$elapsed_time / 1000000
# data$ratio <- data$elapsed_time / data$func_calls
data_ins_hypercall$class <- 'Instrumented with hypercall'
data_ins$class <- 'Instrumented with no hypercall'
data_noins$class <- 'Not Instrumented'

# data = data.frame(
#   not_instrumented=data_noins$elapsed_time,
#   instrumented=data_ins$elapsed_time,
#   instrumented_with_hypercall=data_ins_hypercall$elapsed_time
# )
data <- rbind(data_noins, data_ins, data_ins_hypercall)
# data$elapsed_time <- 1 - (1/data$elapsed_time)
# ins_density <- density(data_ins$elapsed_time) 
# ins_dohypercall_density <- density(data_ins_hypercall$elapsed_time) 
# nosins_density <- density(data_noins$elapsed_time)


p <- ggplot(data, aes(class, elapsed_time))
p <- p + geom_boxplot()  + geom_jitter(width = 0.4)
plot(p)
# plot(1 - (nosins_density$y / ins_dohypercall_density$y))

# mydata <- data.frame(overhead = nosins_density$y - ins_density$y)
# plot <- ggplot(mydata, aes(overhead)) +
#   geom_density(alpha = 0.1) +
#   labs(title = "Hypercall function graph Density") +
#   labs(x="Elapsed time (us)") +
#   labs(fill="Number of entry & exit", colour="#Entry/Exit") +
#   theme_bw()
# plot(plot)

max_overhead <- 1 - max(data_noins$elapsed_time)/ max(data_ins_hypercall$elapsed_time)
min_overhead <- 1 - min(data_noins$elapsed_time)/ min(data_ins_hypercall$elapsed_time)
std_overhead <- 1 - sd(data_noins$elapsed_time)/ sd(data_ins_hypercall$elapsed_time)
mean_overhead <- 1 - mean(data_noins$elapsed_time)/ mean(data_ins_hypercall$elapsed_time)