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
# compute duplicated rows
data_filtered <- ddply(data, .(layer, tracer, maxprime, event),
                       transform,
                       freq = sum(freq),
                       total_event_cost = sum(total_event_cost)/10**3,
                       cost_per_event = sum(total_event_cost)/sum(freq)
)

data_filtered <- unique(data_filtered[c("layer", "tracer", "maxprime", "event", "freq", "total_event_cost", "cost_per_event")])

plot <- ggplot(data_filtered, aes(x=reorder(event, total_event_cost), y = total_event_cost)) +
  geom_bar(aes(fill=tracer), position="stack",stat="identity") +
  scale_y_continuous(breaks = seq(0, max(data_filtered$total_event_cost), 1)) +
  facet_wrap(~maxprime, ncol=4) +
  # coord_flip() +
  # geom_label_repel(aes(y=tracing_events, label=paste(tracing_events,event_type)),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  # geom_text(aes(y=max, label=label ), colour='black', size = 3.4,
  #           position=position_dodge(width=0.9), vjust=-1) +
  
  scale_fill_manual(values = colors) +
  labs(x ="", y ="Exits Cost (us)", fill="Tracing", title=paste("Total cost",sum(data_filtered$total_event_cost))) +
  # scale_fill_manual(values = colors) +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    # legend.title=element_blank(),
    axis.text.x = element_text(angle = -20, hjust = 0, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)