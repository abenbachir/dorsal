#!/usr/bin/env Rscript
library(ggplot2)
library(plyr)
library(scales)
library(ggrepel)
# function_name,exit_time,duration,depth,process
data_freq <- read.table("./bootup-trace/rscript/bootup-func-frequencies.csv", header=T, sep=",")
# data <- read.table("./bootup-trace/dynamic-analysis.csv", header=T, sep=',')
# data_freq <- count(data, c("function_name"))
total <- sum(data_freq$freq)
data_freq$percentage <- round((data_freq$freq/total) * 100, 3)

# write.csv(data_freq, file="./bootup-trace/rscript/bootup-func-frequencies-after-optim-1.csv", row.names = FALSE)

data_freq = subset(data_freq, percentage > 1)
# colors <- c("#0f2054", "#5f2054", "#ff0d54", "#ff8d54")
colors <- c('18.06 %'="#1f2054", '26.57 %'="#3f2054", '21.56 %'="#9f2d54", '14.65 %'="#6f2d54", '14.65 %'="#1f2054",'1.47 %'= "#ff0d54")

data_freq$color[data_freq$percentage >= 9 ] <- sum(subset(data_freq, percentage >= 9 )$percentage)
data_freq$color[data_freq$percentage >= 8 & data_freq$percentage < 9 ] <- sum(subset(data_freq, percentage >= 8 & percentage < 9 )$percentage)
data_freq$color[data_freq$percentage >= 3 & data_freq$percentage < 8 ] <- sum(subset(data_freq, percentage >= 3 & percentage < 8 )$percentage)
data_freq$color[data_freq$percentage >= 2 & data_freq$percentage < 3 ] <- sum(subset(data_freq, percentage >= 2 & percentage < 3 )$percentage)
data_freq$color[data_freq$percentage < 2 ] <- sum(subset(data_freq, percentage < 2 )$percentage)

data_freq$color <- paste(as.character(round(data_freq$color, 2)), '%')

plot <- ggplot(data_freq, aes(reorder(function_name, -freq), fill=color)) +
  geom_bar(aes(weight = freq),  width= 0.7, colour="white") +
  coord_flip() +
  # geom_label_repel(aes(y=freq, label=paste(data_freq$percentage, "%")),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  geom_text(aes(y=freq, label=paste(percentage,'%') ), colour='white',  fontface = "bold", size = 3.4,
            position=position_dodge(width=0.9), hjust=1.1) +
  scale_fill_manual(values = colors) +
  labs(x ="Function name", y ="Frequency") +
  theme_light() +
  theme(
    legend.position = c(0.90,0.84),
    legend.title=element_blank(),
    # axis.text.x = element_blank(),
    # axis.text.x = element_text(angle = 50, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)