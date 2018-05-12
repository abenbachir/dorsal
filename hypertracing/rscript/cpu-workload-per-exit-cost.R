#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
source("./hypertracing/rscript/global.R")
# layer,tracer,workload,configuration,time,event,freq,total_event_cost,cost_per_event
data <- read.table("./hypertracing/data/cpu-workload-exits-cost-1_5000.csv", header=T, sep=",")

data = subset(data, event != 'HLT' )
# data = subset(data, configuration == '1_10000')

data_filtered <- ddply(data, .(layer, tracer, workload, configuration, event),
                       transform,
                       freq = mean(freq),
                       total_event_cost = mean(total_event_cost),
                       cost_per_event = mean(total_event_cost)/mean(freq)
)

data_filtered <- unique(data_filtered[c("layer", "tracer", "configuration", "event", "freq", "total_event_cost", "cost_per_event")])

plot <- ggplot(data_filtered, aes(x=reorder(tracer, freq), y = freq)) +
  geom_bar(aes(fill=tracer), position="dodge",stat="identity") +
  # scale_y_continuous(breaks = seq(0, max(data_filtered$total_event_cost), 1)) +
  facet_wrap(~event, ncol=4, scale="free") +
  # coord_flip() +
  # geom_label_repel(aes(y=tracing_events, label=paste(tracing_events,event_type)),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  # geom_text(aes(y=max, label=label ), colour='black', size = 3.4,
  #           position=position_dodge(width=0.9), vjust=-1) +
  
  # scale_fill_manual(values = colors) +
  labs(x ="", y ="Exits Cost (us)", fill="Tracing", title=paste("Total cost",sum(data_filtered$total_event_cost))) +
  # scale_fill_manual(values = colors) +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    # legend.title=element_blank(),
    axis.text.x = element_text(angle = -20, hjust = 0, vjust=1, size = 8),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)