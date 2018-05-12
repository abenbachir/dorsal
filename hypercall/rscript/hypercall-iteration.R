#!/usr/bin/env Rscript
library(ggplot2)

data1 <- read.table("./hypercall/data/hypercall-cpu-scaling.csv", header=T, sep=",")

data2 <- read.table("./hypercall/data/hypercall-no-cpu-scaling.csv", header=T, sep=",")
# "#ff0d54" # rose
colors <- c("#5f2054","#ff8d54","#ff0d54","#5f2054", "#0f2054",  "#ff8d54") 
max_index = 3300
data1$index <- row(data1)
data2$index <- row(data2)
data1 <- subset(data1, index < max_index)
data2 <- subset(data2, index < max_index)

data1$type <- 'Enabled'
data2$type <- 'Disabled'

data1 <- subset(data1, elapsed_time <= 1600)
data2 <- subset(data2, elapsed_time <= 500)

data <- rbind(data1,data2)


p <- ggplot(data, aes(index, elapsed_time, colour=type)) +
  scale_x_continuous(breaks = seq(0, max(data$index), 1000)) +
  scale_y_continuous(breaks = seq(0, max(data$elapsed_time), 250)) +
  scale_fill_manual(values = colors) +
  scale_colour_manual(values = colors) +
  geom_point(aes(colour=type), size=0.15) +
  geom_smooth(method="loess", span = 0.44,  aes(colour=type), size=0.5) +
  labs(x ="Iteration", y ="Latency (ns)", colour = "CPU Scaling") +
  theme_light() +
  theme(
    legend.position = c(0.84,0.81)
  )

pdf(file="./plots/hypercall-iteration.pdf", width=5.16, height=4.0)
plot(p)
dev.off()

plot(p)