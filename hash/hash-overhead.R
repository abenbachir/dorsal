#!/usr/bin/env Rscript
library(ggplot2)
library(plyr)
data <- read.table("./hash/data.csv", header=T, sep=",")
summary <- ddply(data, c("function_length"), summarise,
      N    = length(elapsed_time),
      mean = mean(elapsed_time),
      median   = median(elapsed_time),
      sd   = sd(elapsed_time),
      se   = sd / sqrt(N)
)


plot <- ggplot(summary, aes(function_length)) +
  # geom_point(size=0.9, aes(y=mean, color="red")) +
  # geom_smooth(se=FALSE, aes(y=mean, color="red")) +

  geom_point(size=0.9, aes(y=median)) +
  geom_smooth(se=FALSE, aes(y=median)) +
  labs(title = 'Hash Function Overhead (median)', x ="Function name length", y ="Nanoseconds", colour = "") +
  theme_bw() +
  theme(
    legend.position = "none"
    # axis.text.x = element_blank(),
    # axis.text.y = element_text(angle = 0, hjust = 1, vjust=1, size = 10),
    # axis.text.x = element_text(angle = 30, hjust = 1, vjust=1, size = 10)
  )
plot(plot)