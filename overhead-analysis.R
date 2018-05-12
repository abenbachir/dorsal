#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)

data <- read.table("./overhead-analysis.csv", header=T, sep=",")

data$time_ms<-data$time
data$time_ms[data$workload != 'cpu'] <- data$time[data$workload != 'cpu']*1000

data <- ddply(data, .(type, workload),
              transform,
              median = round(median(time_ms), 3),
              mean = round(mean(time_ms), 3)
)


# unique_data <- unique(data[c("buffer_size", "transport", "median", "mean", "CPU","show_cpu")])

data_unique <- unique(data[c("type", "workload", "median", "mean")])

print(data_unique)