#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(scales)

y <- 0.1
data <- read.table("./hypercall/data/hypercall-host-disabled.csv", header=T, sep=",")
median <- round(median(data$elapsed_time))
mean <- round(mean(data$elapsed_time))
std <- round(sd(data$elapsed_time))
p <- ggplot() +
  # geom_point(aes(x=median, y=y)) + 
  geom_label_repel(aes(x=median, y=y, label=paste('Median',median,'ns')),
                   min.segment.length = unit(0, "lines"), 
                   nudge_x = 3, 
                   nudge_y = 0.05,
                   color=muted("red")
  ) +
  geom_vline(xintercept = c(median), linetype="dotted", color=muted("red")) +
  geom_density(data=data, aes(elapsed_time), adjust = 5, alpha = 0.5) +
  labs(x ="Nanoseconds", y ="Density", fill = "Host Tracing") +
  # geom_vline(xintercept = c(median1, median2), linetype="dotted") +
  scale_fill_manual(values = colors) +
  xlim(280, 305) +
  theme_light()

plot(p)