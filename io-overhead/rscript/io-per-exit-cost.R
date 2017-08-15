#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
colors <- c("#ff0d54",  "#5f2054", "#2f2054")
# layer,tracer,copies_input_blocks,event,freq,total_event_cost,cost_per_event
data <- read.table("./io-overhead/data/exits-cost2.csv", header=T, sep=",")

data$tracer <- as.character(data$tracer)
data$copied_input_blocks <- paste(data$copied_input_blocks,'blocks')

data = subset(data, event != 'HLT')
data = subset(data, event != 12 & event != 18)

data_filtered <- ddply(data, .(layer, tracer, copied_input_blocks, event),
                       transform,
                       cost_per_event_avrg = mean(cost_per_event),
                       total_event_cost_avrg = mean(total_event_cost)
)

data_filtered <- unique(data_filtered[c("layer", "tracer", "copied_input_blocks", "event", "cost_per_event_avrg", "total_event_cost_avrg")])


plot <- ggplot(data_filtered, aes(x=reorder(event, total_event_cost_avrg), y = total_event_cost_avrg)) +
  geom_bar(aes(fill=tracer), position="dodge",stat="identity") +
  # scale_y_continuous(breaks = seq(0, max(data_filtered$cost_per_event_avrg), 100)) +
  facet_wrap(~copied_input_blocks, ncol=4) +
  # coord_flip() +
  # geom_label_repel(aes(y=tracing_events, label=paste(tracing_events,event_type)),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  # geom_text(aes(y=max, label=label ), colour='black', size = 3.4,
  #           position=position_dodge(width=0.9), vjust=-1) +
  
  scale_fill_manual(values = colors) +
  labs(x ="Virtualization Layers", y ="Exits Cost (ms)", fill="Tracing") +
  # scale_fill_manual(values = colors) +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    # legend.title=element_blank(),
    axis.text.x = element_text(angle = 40, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)