#!/usr/bin/env Rscript
# function_name,parent,process,exit_timestamp,depth,duration
library(latticeExtra)
library(stringi)
library(ggplot2)
library(plyr)
library(scales)
data <- read.table("./bootup-trace/dynamic-analysis.csv", header=T, sep=",")


data <- head(data, 100)

start_timestamp <- unlist(head(data, 1))[5]

data$entry_timestamp <- data$exit_timestamp - data$duration

data$entry_time <- data$entry_timestamp - start_timestamp

# plot = xyplot( function_name~entry_time,
#             data=data,
#             xlab=" date",
#             ylab="Developers",
#             # auto.key = list(column=2, text = c("Not Travis Data", "Travis Data"), space = "top"),
#             groups = pid,
#             cex=0.5,
#             pch=20,
#             grid = TRUE
# )
data <- subset(data, pid == 1)
data$pid <- as.character(data$pid)

plot <- ggplot(data, aes(x=entry_time, y=depth, color=function_name)) +
  # geom_point(aes(x=entry_time)) +
  geom_errorbarh(aes(xmax = entry_time, xmin = entry_time + duration), height = .1) +
  # coord_flip() +
  # geom_text(aes(y=percentage, label=paste(percentage,'%') ), color="#3f2054",  fontface = "bold",
  #           size = 3.5, position=position_dodge(width=0.9), vjust=-1) +
  # scale_fill_manual(values = colors) +
  # labs(x ="Function prefix", y ="%") +
  theme_light() +
  theme(
    legend.position = "none",
    legend.title=element_blank(),
    # axis.text.x = element_blank(),
    # axis.text.x = element_text(angle = 50, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)
