#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)

data1 <- read.table("./interVM-benchmark/data-hypercall.csv", header=T, sep=",")
data2 <- read.table("./interVM-benchmark/data-virtio.csv", header=T, sep=",")
data3 <- read.table("./interVM-benchmark/data-nahanni.csv", header=T, sep=",")
data4 <- read.table("./interVM-benchmark/data-nahanni-warmup.csv", header=T, sep=",")


colors <- c( "#af2054", "dodgerblue2", "darkorange2", "#3faf1f")
data1$transport <- 'Hypercall'
data2$transport <- 'Virtio-serial'
data3$transport <- 'Nahanni'
data4$transport <- 'Nahanni with warmup'

data <- rbind(data2, data3, data4)
data$CPU <- 1
data$show_cpu <- FALSE
data <- rbind(data1, data)

data <- ddply(data, .(buffer_size, transport),
              transform,
              median = round(median(througthput), 2),
              mean = round(mean(througthput), 2)
)

unique_data <- unique(data[c("buffer_size", "transport", "median", "mean", "CPU","show_cpu")])

unique_data$througthput <- unique_data$mean
unique_data$buffer_size_label <- as.character(round(unique_data$buffer_size,4))

unique_data$label <- paste(unique_data$CPU,"CPU")
unique_data$label[unique_data$show_cpu == FALSE] <- ''

p <- ggplot(unique_data, aes(x=reorder(buffer_size_label, buffer_size), y=througthput, group=transport)) +
  scale_y_continuous(breaks = seq(0, max(unique_data$througthput), 10)) +
  geom_point(aes(shape=transport, color=transport), size=2) +
  geom_line(aes(color=transport)) +
  geom_label_repel(aes(y=througthput, label=label),
                   size = 2.5, segment.size = 0.5, colour="white", segment.color="#af2054",  fill = "#af2054",
                   min.segment.length = unit(0, "lines"), nudge_x = 0.75, nudge_y = 10
  ) +
  scale_color_manual(values = colors, name = "Transport") +
  scale_shape_manual(values=c(4, 15, 16, 17), name = "Transport")+
  # geom_hline(yintercept = c(2.24), linetype="dotted") +
  labs(x ="Message size", y ="Throughput (Gbps)") +
  
  theme_light()+
  theme(
    # legend.position="none",
    legend.position=c(.18,.82),
    axis.text.x = element_text(angle = 40, hjust = 1, vjust=1, size = 10)
    # axis.text.y = element_text(size=12),
    # axis.text.x = element_text(size=12)
    # axis.text.y = element_blank()
  )

pdf(file="./plots/shared-transport-comparison.pdf", width=5.3, height=4.8)
plot(p)
dev.off()
plot(p)
