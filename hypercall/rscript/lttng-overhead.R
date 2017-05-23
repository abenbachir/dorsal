#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)

data1 <- read.table("./hypercall/data/hypercall-host-disabled.csv", header=T, sep=",")
data2 <- read.table("./hypercall/data/hypercall-host-enabled-lttng2-10.csv", header=T, sep=",")
data3 <- read.table("./hypercall/data/hypercall-host-enbaled-lttng2-7.csv", header=T, sep=",")
data4 <- read.table("./hypercall/data/hypercall-host-enabled-ftrace.csv", header=T, sep=",")
data5 <- read.table("./hypercall/data/hypercall-host-enabled-ebpf.csv", header=T, sep=",")

colors <- c("#0f2d54", "#5f2054","#af2d54", "#ff2d54", "#ff5d54")
data1$tracer <- "None"
data2$tracer <- "Lttng 2.10 (hypercall only)"
data4$tracer <- "lttng (exit+hypercall+entry)"
data5$tracer <- "eBPF/bcc (exit+hypercall+entry)"

median1 <- round(median(data1$elapsed_time))
median2 <- round(median(data2$elapsed_time))
median3 <- round(median(data3$elapsed_time))
median4 <- round(median(data4$elapsed_time))
median5 <- round(median(data5$elapsed_time))

# data <- merge(data1, data2, all=TRUE)
# data <- merge(data, data3, all=TRUE)
# data <- merge(data, data4, all=TRUE)
# data <- merge(data, data5, all=TRUE)

# y1 <- 0.49
# y2 <- 0.13
# y3 <- 0.135
# y4 <- 0.43
# y5 <- 0.23
# p <- ggplot() +
#   
#   geom_point(aes(x=median1, y=y1)) + 
#   geom_label_repel(aes(x=median1, y=y1, label=paste(median1,'ns')), nudge_x = 10) +
#   
#   geom_point(aes(x=median2, y=y2)) + 
#   geom_label_repel(aes(x=median2, y=y2, label=paste(median2,'ns')), nudge_x = 10) +
#   
#   geom_point(aes(x=median3, y=y3)) + 
#   geom_label_repel(aes(x=median3, y=y3, label=paste(median3,'ns')), nudge_x = 10) +
#   
#   geom_point(aes(x=median4, y=y4)) + 
#   geom_label_repel(aes(x=median4, y=y4, label=paste(median4,'ns')), nudge_x = 10) +
#   
#   geom_point(aes(x=median5, y=y5)) + 
#   geom_label_repel(aes(x=median5, y=y5, label=paste(median5,'ns')), nudge_x = 10) +
#   
#   geom_density(data=data, aes(elapsed_time, fill = tracer), adjust = 5, alpha = 0.5) +
#   labs(x ="Nanoseconds", y ="Density", fill = "Host Tracing") +
#   geom_vline(xintercept = c(median1, median2, median3, median4), linetype="dotted") +
#   # scale_fill_manual(values = colors) +
#   xlim(275, 700) +
#   theme_light()
# 
# plot(p)