#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)

data1 <- read.table("./interVM-benchmark/data-hypercall.csv", header=T, sep=",")
data2 <- read.table("./interVM-benchmark/data-virtio.csv", header=T, sep=",")
data3 <- read.table("./interVM-benchmark/data-nahanni.csv", header=T, sep=",")
data4 <- read.table("./interVM-benchmark/data-nahanni-warmup.csv", header=T, sep=",")


colors <- c( "#af2054", "dodgerblue2", "#00af1f", "#3faf1f")
data1$transport <- 'Hypercall'
data2$transport <- 'Virtio-serial'
data3$transport <- 'Nahanni'
data4$transport <- 'Nahanni with warmup'

data <- rbind(data2, data3)
data$CPU <- 1
data$show_cpu <- FALSE
data <- rbind(data1, data)

data <- ddply(data, .(buffer_size, transport),
              transform,
              median = round(median(througthput), 2),
              mean = round(mean(througthput), 2)
)

unique_data <- unique(data[c("buffer_size", "transport", "median", "mean", "CPU","show_cpu")])

unique_data <- subset(unique_data, buffer_size < 4096000)
unique_data$througthput <- unique_data$mean
unique_data$buffer_size_label <- as.character(round(unique_data$buffer_size,4))

unique_data$label <- paste(unique_data$CPU,"CPUs")
unique_data$label[unique_data$show_cpu == FALSE] <- ''

for(i in 1:nrow(unique_data)) {
  row <- unique_data[i,]
  if(row$buffer_size < 1000)
  {
    unique_data[i,]$buffer_size_label <- paste(row$buffer_size,'B', sep=' ')
  }else if(row$buffer_size < 1000000){
    size = floor(row$buffer_size/1000)
    unique_data[i,]$buffer_size_label <- paste(size,'KB', sep=' ')
  }else if(row$buffer_size < 1000000000){
    size = floor(row$buffer_size/1000000)
    unique_data[i,]$buffer_size_label <- paste(size,'MB', sep=' ')
  }
}

p <- ggplot(unique_data, aes(x=reorder(buffer_size_label, buffer_size), y=througthput, group=transport)) +
  scale_y_continuous(breaks = seq(0, max(unique_data$througthput), 10)) +
  geom_point(aes(shape=transport, color=transport), size=3) +
  geom_line(aes(linetype=transport,color=transport)) +
  # geom_label_repel(aes(y=througthput, label=label),
  #                  size = 2.5, segment.size = 0.5, colour="white", segment.color="#7f2054",  fill = "#7f2054",
  #                  min.segment.length = unit(0, "lines"), nudge_x = -0.25, nudge_y = 5
  # ) +
  
  geom_segment(aes(x=1,xend=11,y=8.92,yend=8.92), linetype="solid", color="#af2054", size=0.28) +
  geom_segment(aes(x=1,xend=11,y=17.92,yend=17.92), linetype="solid", color="#af2054", size=0.28) +
  
  annotate("label", x = 10, y = 2.25, label = " 1 CPU ", color="white",fill="#af2054", label.padding = unit(0.3, "lines"),size = 2.5) +
  annotate("label", x = 10, y = 8.92, label = " Hypercall: 4 CPUs ", color="white",fill="#af2054", label.padding = unit(0.3, "lines"),size = 2.5) +
  annotate("label", x = 10, y = 17.92, label = " Hypercall: 8 CPUs ", color="white", fill="#af2054", label.padding = unit(0.3, "lines"),size = 2.5) +
  
  scale_color_manual(values = colors, name = "Transport") +
  scale_shape_manual(values=c(4, 15, 17,16), name = "Transport")+
  scale_linetype_manual(values=c( "solid", "dashed", "twodash"), name = "Transport")+
  # geom_hline(yintercept = c(2.24), linetype="dotted") +
  labs(x ="Message size", y ="Throughput (Gbps)") +
  
  theme_light()+
  theme(
    # legend.position="none",
    legend.position=c(.15,.85),
    axis.text.x = element_text(angle = 40, hjust = 1, vjust=1, size = 10)
    # axis.text.y = element_text(size=12),
    # axis.text.x = element_text(size=12)
    # axis.text.y = element_blank()
  )

pdf(file="./plots/shared-transport-comparison.pdf", width=5.3, height=4.8)
plot(p)
dev.off()
plot(p)
