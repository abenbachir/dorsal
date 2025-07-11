#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
# write.csv(data1, file="./hypercall/data/hypercall-host-disabled.csv", row.names = FALSE)

# "#ff0d54" # rose
colors <- c("#5f2054", "#0f2054",  "#ff8d54") 

baseline_data <- read.table("./hypercall/data/hypercall-host-disabled.csv", header=T, sep=",")
baseline <- median(baseline_data$elapsed_time)
baseline_data$tracer <- 'Lttng 2.10'
baseline_data$mode <- 'Baseline'

data1 <- read.table("./hypercall/data/hypercall-host-lttng2.10.csv", header=T, sep=",")
data1$mode <- 'Hypercall'
data2 <- read.table("./hypercall/data/hypercall-host-lttng-3-events.csv", header=T, sep=",")
data2$mode <- 'Exit + Hypercall + Entry'
data3 <- read.table("./hypercall/data/hypercall-host-lttng-kernel-module.csv", header=T, sep=",")
data3$mode <- 'Events aggregation'


data1$tracer <- 'Lttng 2.10'
data2$tracer <- 'Lttng 2.10'
data3$tracer <- 'Lttng 2.10'
data <- rbind(data1, data2, data3)

data <- ddply(data,"mode",
              transform,
              median = round(median(elapsed_time))
)
unique_data <- unique(data[c("tracer", "mode", "median")])
unique_data$overhead <- round(100*(1 - baseline/unique_data$median))

plot <- ggplot(unique_data, aes(x=reorder(mode, median), y=median)) +
  geom_bar(aes(fill=mode),position="dodge",stat="identity") +
  geom_text(aes(label=paste(overhead,'%') ), colour='white',
            # label.padding = unit(0.5, "lines"),
            # label.r = unit(0.7, "lines"),
            # label.size = 0, 
            # size = 5,
            position=position_dodge(width=0.9), vjust=2) +
  # coord_flip() +
  scale_fill_manual(values = colors) +
  geom_hline(yintercept = c(baseline), linetype="dashed", color="white") +
  annotate("text", x = 1:3, y = baseline - 20, label = "Baseline", color="white", fill="black",
           label.padding = unit(0.35, "lines"), size = 3.5) +
 
  labs(x ="", y ="Latency (ns)", fill = "Traced events") +
  
  theme_light()+
  theme(
    legend.position="none"
    # axis.text.y = element_text(size=12),
    # axis.text.x = element_text(size=14)
  )

pdf(file="./plots/event-aggregation.pdf", width=5.16, height=4.3)
plot(plot)

dev.off()