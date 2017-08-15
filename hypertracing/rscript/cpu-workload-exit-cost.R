#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
source("./hypertracing/rscript/global.R")
# layer,tracer,workload,configuration,time,event,freq,total_event_cost,cost_per_event
data <- read.table("./hypertracing/data/cpu-workload-exits-cost-1_1000.csv", header=T, sep=",")

data = subset(data, event != 'HLT' & event != 'VMCALL')
# data = subset(data, configuration == '1_10000')
# data = subset(data, tracer == 'None')
data_filtered <- ddply(data, .(layer, tracer, workload, configuration, event),
                       transform,
                       total_event_cost_avg = mean(total_event_cost)
)

data_filtered <- unique(data_filtered[c("layer", "tracer", "workload", "configuration", "time", "event", "total_event_cost_avg")])

data_filtered <- ddply(data_filtered, .(layer, tracer, workload, configuration),
                       transform,
                       total_exits_cost = sum(total_event_cost_avg)/10**6,
                       time_avg = mean(time)/10**6
)
data_filtered <- unique(data_filtered[c("layer", "tracer", "workload", "configuration", "time_avg","total_exits_cost")])

df2 <- melt(data_filtered, id.vars=c("time_avg", "total_exits_cost"))

plot <- ggplot(data_filtered, aes(x=reorder(tracer, total_exits_cost), y = total_exits_cost)) +
  geom_bar(aes(fill=tracer), position="dodge",stat="identity") +
  # scale_y_continuous(breaks = seq(0, max(data_filtered$total_exits_cost), 100)) +
  facet_wrap(~configuration, ncol=2) +
  # coord_flip() +
  # geom_label_repel(aes(y=tracing_events, label=paste(tracing_events,event_type)),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  # geom_text(aes(y=max, label=label ), colour='black', size = 3.4,
  #           position=position_dodge(width=0.9), vjust=-1) +
  
  # scale_fill_manual(values = colors) +
  labs(x ="Virtualization Layers", y ="Exits Cost (us)", fill="Tracing") +
  # scale_fill_manual(values = colors) +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    # legend.title=element_blank(),
    # axis.text.x = element_text(angle = 40, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)