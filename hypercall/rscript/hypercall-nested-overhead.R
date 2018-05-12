#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
# write.csv(data1, file="./hypercall/data/hypercall-host-disabled.csv", row.names = FALSE)

data1 <- read.table("./hypercall/data/hypercall-benchmark-l1.csv", header=T, sep=",")
data2 <- read.table("./hypercall/data/hypercall-benchmark-l2.csv", header=T, sep=",")
data3 <- read.table("./hypercall/data/hypercall-benchmark-l3.csv", header=T, sep=",")

data11 <- read.table("./hypercall/data/hypercall-benchmark-l1.csv", header=T, sep=",")
data22 <- read.table("./hypercall/data/hypercall-nested-patch-l2.csv", header=T, sep=",")
data33 <- read.table("./hypercall/data/hypercall-nested-patch-l3.csv", header=T, sep=",")

baseline <- median(data1$elapsed_time)


data1$layer <- 'L1'
data2$layer <- 'L2'
data3$layer <- 'L3'
data11$layer <- 'L1'
data22$layer <- 'L2'
data33$layer <- 'L3'

multiple = "Exit multiplication"
single = "Guest single exit"
optimization = "Nested single exit (L0 optimization)"
data2$mode <- multiple
data3$mode <- multiple
data1$mode <- single
data11$mode <- optimization
data22$mode <- optimization
data33$mode <- optimization

# colors <- c( "#af2054", "#5f2054", "#ff0d54")
# colors <- c("#5f2054", "#0f2054",  "#ff8d54")
colors <- c( "#ef0d54", "#2571b0", "#5f2054")
# colors <- c(multiple = "gray10", single = "#cf1f54", optimization="dodgerblue2")
  
data <- rbind(data1, data2, data3, data22, data33)

data <- ddply(data, .(layer,mode),
              transform,
              median = round(median(elapsed_time))
)

unique_data <- unique(data[c("layer", "mode", "median")])
unique_data$ratio <- ''
unique_data$overhead <- round((unique_data$median/baseline -1)*100, 2)
unique_data$time_label <- ''


for(i in 1:nrow(unique_data)) {
  row <- unique_data[i,]
  unique_data[i,]$time_label <- paste(row$median,'ns')
  if(row$layer == 'L1')
    next
  
  if(row$mode == multiple){
    unique_data[i,]$time_label <- paste(round(row$median/1000,1),'us')
    unique_data[i,]$ratio <- paste('(x',round(row$median/baseline),')',sep='')
    if(row$layer == 'L3')
      unique_data[i,]$median <- row$median/110
    else
      unique_data[i,]$median <- row$median/11
    
  }else{
    unique_data[i,]$ratio <- paste('(',round(row$overhead,2),'%)\n [ KVM patch ]',sep='')
  }
}

p <- ggplot(unique_data, aes(x=reorder(layer, median), y=median)) +
  geom_bar(aes(fill=mode), position="stack", stat="identity") +
  geom_text(aes(label=paste(time_label, ratio, sep=' ' )),
            colour='white',  size = 3.4,
            position=position_dodge(width=0.1), vjust=1.3) +
  # coord_flip() +
  scale_fill_manual(values = colors) +
  # geom_hline(yintercept = c(baseline), linetype="dotted") +
  labs(x ="Virtualization layers", y ="Overhead (ns)", fill = "") +
  
  theme_light()+
  theme(
    # legend.position="none",
    legend.position=c(.3,.86)
    # axis.text.y = element_text(size=12),
    # axis.text.x = element_text(size=12)
    # axis.text.y = element_blank()
  )

pdf(file="./plots/hypercall-nested-overhead.pdf", width=5.16, height=4.6)
plot(p)

dev.off()
plot(p)
