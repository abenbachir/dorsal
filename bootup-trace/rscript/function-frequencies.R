#!/usr/bin/env Rscript
library(ggplot2)
library(plyr)
library(scales)
library(ggrepel)
# function_name,exit_time,duration,depth,process
data_freq <- read.table("./bootup-trace/rscript/bootup-func-frequencies.csv", header=T, sep=",")
# data <- read.table("./bootup-trace/rscript/static-analysis.csv", header=T, sep=",")
# data_freq <- count(data, c("function_name"))
total <- 168921670/2
data_freq$percentage <- round((data_freq$freq/total) * 100, 2)

data_freq = subset(data_freq, freq > 300000)

colors <- c("#9f2d54", "#6f2d54", "#3f2054")
data_freq$color[data_freq$percentage > 5 ] <- sum(subset(data_freq, percentage > 5 )$percentage)
data_freq$color[data_freq$percentage >= 1 & data_freq$percentage < 5 ] <- sum(subset(data_freq, percentage >= 1 & percentage < 5 )$percentage)
data_freq$color[data_freq$percentage < 1 ] <- sum(subset(data_freq, percentage < 1 )$percentage)

data_freq$color <- paste(as.character(data_freq$color), '%')
plot <- ggplot(data_freq, aes(reorder(function_name, -freq), fill=color)) +
  geom_bar(aes(weight = freq),  width= 0.7, colour="transparent") +
  coord_flip() +
  # geom_point(aes(y = freq), size = 1, colour=muted("black")) +
  geom_label_repel(aes(y=freq, label=paste(data_freq$percentage, "%")),
                   size = 3, segment.size = 0.3, colour="black", fill="white",
                   min.segment.length = unit(0, "lines"), nudge_x = 0
                   ) +
  scale_fill_manual(values = colors) +
  labs(x ="Function name", y ="Frequency") +
  theme_light() +
  theme(
    legend.position = "top",
    legend.title=element_blank(),
    # axis.text.x = element_blank(),
    # axis.text.x = element_text(angle = 50, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)