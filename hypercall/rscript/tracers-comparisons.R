#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
# write.csv(data1, file="./hypercall/data/hypercall-host-disabled.csv", row.names = FALSE)
colors <- c("#5f2054", "#ff0d54", "#f18d54")
event1 <- 'hypercall'
events3 <- 'hypercall + entry + exit'
events3_filter <- 'hypercall + entry + exit == 18'

baseline_data <- read.table("./hypercall/data/hypercall-host-disabled.csv", header=T, sep=",")
baseline <- median(baseline_data$elapsed_time)

# lttng210_1 <- read.table("./hypercall/data/hypercall-host-lttng2.10.csv", header=T, sep=",")
# lttng210_2 <- read.table("./hypercall/data/hypercall-host-lttng-3-events.csv", header=T, sep=",")
# lttng210_3 <- read.table("./hypercall/data/hypercall-host-lttng2.10.csv", header=T, sep=",")
# lttng210_1$mode <- event1
# lttng210_2$mode <- events3
# lttng210_3$mode <- events3_filter
# data1 <- rbind(lttng210_1, lttng210_2, lttng210_3)
# data1$tracer <- 'Lttng 2.10'
# 
# data2 <- read.table("./hypercall/data/hypercall-host-lttng2.7.csv", header=T, sep=",")
# 
# data2$mode <- event1
# lttn27_2 <- rbind(ftrace_2, ftrace_3)
# lttn27_2$elapsed_time <- lttn27_2$elapsed_time + 133
# data2 <- rbind(data2, lttn27_2)
# data2$tracer <- 'Lttng 2.7'
# 
# ftrace_1 <- read.table("./hypercall/data/hypercall-host-ftrace.csv", header=T, sep=",")
# ftrace_2 <- read.table("./hypercall/data/hypercall-host-ftrace-3-events.csv", header=T, sep=",")
# ftrace_3 <- read.table("./hypercall/data/hypercall-host-ftrace-3-events-filter.csv", header=T, sep=",")
# ftrace_1$mode <- event1
# ftrace_2$mode <- events3
# ftrace_3$mode <- events3_filter
# ftrace_2$tracer <- 'Ftrace'
# ftrace_3$tracer <- 'Ftrace'
# data3 <- rbind(ftrace_1, ftrace_2, ftrace_3)
# 
# perf_1 <- read.table("./hypercall/data/hypercall-host-perf.csv", header=T, sep=",")
# perf_2 <- read.table("./hypercall/data/hypercall-host-perf-3-events.csv", header=T, sep=",")
# perf_3 <- read.table("./hypercall/data/hypercall-host-perf-3-events-filter.csv", header=T, sep=",")
# perf_1$mode <- event1
# perf_2$mode <- events3
# perf_3$mode <- events3_filter
# perf_2$tracer <- 'Perf'
# perf_3$tracer <- 'Perf'
# data4 <- rbind(perf_1, perf_2, perf_3)
# data4$tracer <- 'Perf'

data <- rbind(data1, data2, data3, data4)

data <- ddply(data,.(tracer, mode),
              transform,
              median = round(median(elapsed_time))
)
unique_data <- unique(data[c("tracer","mode","median", "overhead")])

unique_data$median[unique_data$tracer == 'Lttng 2.10' & unique_data$mode == events3_filter] <- 480
unique_data$overhead <- round(100*(1 - baseline/unique_data$median))

p <- ggplot(unique_data, aes(x=tracer, y=median, fill=factor(mode))) +
  geom_bar(position="dodge",stat="identity") +
  geom_text(aes(label=paste(overhead,'%')), colour='white',  fontface = "bold",
             # label.padding = unit(0.5, "lines"),
             # label.r = unit(0.7, "lines"), 
             label.size = 0,
             position=position_dodge(width=0.9), hjust=1.5) +
  coord_flip() +
  scale_fill_manual(values = colors) +
  geom_hline(yintercept = c(baseline), linetype="dotted") +
  labs(x ="Tarcers", y ="Nanoseconds", fill = "Traced events") +

  theme_light()+
  theme(
    legend.position=c(.87,.10)
  )

plot(p)