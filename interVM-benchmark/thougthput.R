#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)

data1 <- read.table("./interVM-benchmark/data-hypercall.csv", header=T, sep=",")
data2 <- read.table("./interVM-benchmark/data-virtio.csv", header=T, sep=",")
data3 <- read.table("./interVM-benchmark/data-nahanni.csv", header=T, sep=",")

baseline <- median(data1$elapsed_time)

colors <- c( "#af2054", "dodgerblue2", "darkorange2")
data1$transport <- 'Hypercall'
data2$transport <- 'Page sharing (virtio-serial)'
data2$CPU <- 1
data3$transport <- 'Memory sharing (nahanni)'
data3$CPU <- 1


data <- rbind(data1, data2, data3)

data <- ddply(data, .(buffer_size, transport),
              transform,
              median = round(median(througthput), 2),
              mean = round(mean(througthput), 2)
)


unique_data <- unique(data[c("buffer_size", "transport", "median", "mean", "CPU")])

unique_data$througthput <- unique_data$mean

unique_data$buffer_size_label <- as.character(round(unique_data$buffer_size/1000,1))

p <- ggplot(unique_data, aes(x=reorder(buffer_size_label, buffer_size), y=througthput, group=transport, colour=transport)) +
  geom_point() +
  geom_line() +
  # geom_text(aes(label=paste(time_label, ratio, sep=' ' )),
  #           colour='white',  size = 3.4,
  #           position=position_dodge(width=0.1), vjust=1.9) +
  # coord_flip() +
  scale_colour_manual(values = colors) +
  geom_hline(yintercept = c(2.24), linetype="dotted") +
  labs(x ="Message size", y ="Throughput (Gbps/s)", colour = "Transport") +
  
  theme_light()+
  theme(
    # legend.position="none",
    legend.position=c(.13,.85),
    axis.text.x = element_text(angle = 40, hjust = 1, vjust=1, size = 10),
    # axis.text.y = element_text(size=12),
    # axis.text.x = element_text(size=12)
    # axis.text.y = element_blank()
  )

pdf(file="./plots/shared-transport-comparison.pdf", width=5.5, height=4.6)
plot(p)

dev.off()
plot(p)