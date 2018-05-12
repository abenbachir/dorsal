#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)

# level,time,events
data <- read.table("./bootup-trace/rscript/boot-stat.csv", header=T, sep=",")

bootup_time_baseline = 868.520 #ms
bootup_time = 2608.425825 # ms

bootup_overhead <- (1 - (bootup_time_baseline/bootup_time))*100

data$bootup_percent <- (data$time/bootup_time) * 100

data$overhead <- round((data$bootup_percent/100 * bootup_overhead/100) * 100, 3)
# write.csv(data, file="./bootup-trace/rscript/boot-stat.csv", row.names = FALSE)


plot <- ggplot(data, aes(reorder(level, -time))) +
  geom_bar(aes(weight = overhead),  width= 0.7, colour="white") +
  coord_flip() +
  # geom_label_repel(aes(y=freq, label=paste(data_freq$percentage, "%")),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  geom_text(aes(y=overhead, label=paste(overhead,'%') ), colour='black', size = 3.4,
            position=position_dodge(width=0.9), hjust=-0.1) +
  # scale_fill_manual(values = colors) +
  labs(x ="Bootup level", y ="Overhead") +
  theme_light() +
  theme(
    legend.position = c(0.94,0.91),
    legend.title=element_blank(),
    # axis.text.x = element_blank(),
    # axis.text.x = element_text(angle = 20, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)