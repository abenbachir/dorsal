#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)

# level,time,events
data <- read.table("./hypertracing/data/old/abder-pc-dd.csv", header=T, sep=",")
data$time <- data$time
data$tracing_enabled <- as.character(data$tracing_enabled)
data <- ddply(data, .(hostname, tracing_enabled),
              transform,
              t_median = median(time),
              t_mean = mean(time)
)

unique_data <- unique(data[c("hostname", "tracing_enabled", "t_median", "t_mean")])

plot <- ggplot(unique_data, aes(x=reorder(hostname, t_median), y = t_median)) +
  geom_bar(aes(fill=hostname), position="dodge",stat="identity") +
  facet_wrap(~tracing_enabled) +
  # coord_flip() +
  # geom_label_repel(aes(y=freq, label=paste(data_freq$percentage, "%")),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  # geom_text(aes(y=overhead, label=paste(overhead,'%') ), colour='black', size = 3.4,
  #           position=position_dodge(width=0.9), hjust=-0.1) +
  # scale_fill_manual(values = colors) +
  labs(x ="Nested level", y ="Time (ms)") +
  theme_light() 
  # theme(
  #   legend.position = c(0.94,0.91),
  #   legend.title=element_blank(),
  #   # axis.text.x = element_blank(),
  #   # axis.text.x = element_text(angle = 20, hjust = 1, vjust=1, size = 10),
  #   axis.text.y = element_text(margin = margin(t=2,b=1))
  # )
plot(plot)