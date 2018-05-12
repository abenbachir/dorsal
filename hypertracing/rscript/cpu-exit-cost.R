#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
colors <- c("#ff0d54",  "#5f2054", "#2f2054")
# layer,tracer,maxprime,event,freq,total_event_cost,cost_per_event
data <- read.table("./io-overhead/data/exits-cost-cpu.csv", header=T, sep=",")
data$maxprime <- paste(data$maxprime,'max prime')

data = subset(data, event != 'VMCALL')
data = subset(data, tracer != 'sysbench' & tracer != 'dd')
# data = subset(data, event != 12 & event != 18)

# compute duplicated rows
data_filtered <- ddply(data, .(layer, tracer, maxprime, event),
                       transform,
                       freq = sum(freq),
                       total_event_cost = sum(total_event_cost),
                       cost_per_event = sum(total_event_cost)/sum(freq)
)

data_filtered <- unique(data_filtered[c("layer", "tracer", "maxprime", "event", "freq","total_event_cost")])

data_filtered <- ddply(data_filtered, .(layer, tracer, maxprime),
                       transform,
                       total_exit_freq = sum(freq),
                       total_exits_cost = sum(total_event_cost)/10**6
)

data_filtered <- unique(data_filtered[c("layer", "tracer", "maxprime", "total_exits_cost", "total_exit_freq")])


plot <- ggplot(data_filtered, aes(x=reorder(layer, total_exits_cost), y = total_exits_cost)) +
  geom_bar(aes(fill=tracer), position="dodge",stat="identity") +
  # scale_y_continuous(breaks = seq(0, max(data_filtered$total_exits_cost), 100)) +
  facet_wrap(~maxprime, ncol=4) +
  # coord_flip() +
  # geom_label_repel(aes(y=tracing_events, label=paste(tracing_events,event_type)),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  # geom_text(aes(y=max, label=label ), colour='black', size = 3.4,
  #           position=position_dodge(width=0.9), vjust=-1) +
  
  # scale_fill_manual(values = colors) +
  labs(x ="Virtualization Layers", y ="Exits Cost (ms)", fill="Tracing") +
  scale_fill_manual(values = colors) +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    # legend.title=element_blank(),
    # axis.text.x = element_text(angle = 40, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)