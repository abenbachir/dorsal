#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
# write.csv(data1, file="./hypercall/data/hypercall-host-disabled.csv", row.names = FALSE)

data1 <- read.table("./hypercall/data/hypercall-host-disabled.csv", header=T, sep=",")
data2 <- read.table("./hypercall/data/hypercall-host-lttng2.10.csv", header=T, sep=",")
data3 <- read.table("./hypercall/data/hypercall-host-lttng2.7.csv", header=T, sep=",")
data4 <- read.table("./hypercall/data/hypercall-host-ftrace.csv", header=T, sep=",")
data5 <- read.table("./hypercall/data/hypercall-host-perf.csv", header=T, sep=",")

colors <- c("#0f2054", "#5f2054","#ef2daf", "#ff0d54", "#ff8d54")
data1$tracer <- 'Baseline'
data <- rbind(data1, data2, data3, data4, data5)

densMode <- function(x){
  td <- density(x, adjust=5)
  maxDens <- which.max(td$y)
  list(x=td$x[maxDens], y=td$y[maxDens])
}
data <- ddply(data,"tracer",
              transform,
              val_median = round(median(elapsed_time)),
              val_mean = round(mean(elapsed_time)),
              med = densMode(elapsed_time)
        )
xdat <- unique(data[c("tracer","val_median", "val_mean", "med.x","med.y")])

xdat$med.y[xdat$tracer == 'Ftrace'] <- 0.23
xdat$med.y[xdat$tracer == 'Baseline'] <- 0.485
xdat$med.y[xdat$tracer == 'Lttng 2.10'] <- 0.1
xdat$med.y[xdat$tracer == 'Lttng 2.7'] <- 0.09
xdat$med.y[xdat$tracer == 'Perf'] <- 0.22

p <- ggplot() +
  # geom_point(data=xdat, aes(x=med.x, y=med.y)) +
  geom_label_repel(data=xdat, aes(x=val_median, y=med.y, label=paste(tracer,'[',val_median,'ns ]')), nudge_x = 20,nudge_y = 0.05) +
  geom_density(data=data, aes(elapsed_time, fill = tracer), adjust=5, alpha = 0.7) +
  
  # geom_vline(xintercept = c(median1, median2, median3, median4, median5), linetype="dotted") +
  scale_fill_manual(values = colors) +
  labs(x ="Nanoseconds", y ="Density", fill = "Host Tracers") +
  xlim(280, 490) +
  theme_light()

plot(p)