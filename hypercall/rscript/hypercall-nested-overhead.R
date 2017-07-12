#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
# write.csv(data1, file="./hypercall/data/hypercall-host-disabled.csv", row.names = FALSE)

data1 <- read.table("./hypercall/data/hypercall-benchmark-l1.csv", header=T, sep=",")
data2 <- read.table("./hypercall/data/hypercall-benchmark-l2.csv", header=T, sep=",")
data3 <- read.table("./hypercall/data/hypercall-benchmark-l3.csv", header=T, sep=",")

baseline <- median(data1$elapsed_time)

colors <- c( "#5f2054", "#ff0d54", "#ff8d54")
data1$layer <- 'L1'
data2$layer <- 'L2'
data3$layer <- 'L3'
data <- rbind(data1, data2, data3)

data <- ddply(data,"layer",
              transform,
              median = round(median(elapsed_time))
)

unique_data <- unique(data[c("layer", "median")])
unique_data$overhead <- round(unique_data$median/baseline)

p <- ggplot(unique_data, aes(x=reorder(layer, median), y=log(median))) +
  geom_bar(aes(fill=layer),position="dodge",stat="identity") +
  geom_text(aes(label=paste(paste(round(median/1000,2),'us',sep=' '), paste('x',overhead,sep=''), sep='\n' )), colour='white',  fontface = "bold",
            # label.padding = unit(0.5, "lines"),
            # label.r = unit(0.7, "lines"),
            # label.size = 0, 
            size = 5,
            position=position_dodge(width=0.9), vjust=2) +
  # coord_flip() +
  scale_fill_manual(values = colors) +
  # geom_hline(yintercept = c(baseline), linetype="dotted") +
  labs(x ="", y ="Nanoseconds", fill = "Traced events") +
  
  theme_light()+
  theme(
    legend.position="none",
    axis.text.y = element_text(size=12),
    axis.text.x = element_text(size=14)
  )

plot(p)