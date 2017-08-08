#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
colors <- c("#ff0d54",  "#5f2054")
# layer,tracing_enabled,type,freq,event
data_10 <- read.table("./io-overhead/data/io-exits-10.csv", header=T, sep=",")
data_100 <- read.table("./io-overhead/data/io-exits-100.csv", header=T, sep=",")
data_1000 <- read.table("./io-overhead/data/io-exits-1000.csv", header=T, sep=",")

data_10$copied_input_blocks <- 10
data_100$copied_input_blocks <- 100
data_1000$copied_input_blocks <- 1000

data <- rbind(data_10, data_100, data_1000)

data$tracing_enabled <- as.character(data$tracing_enabled)
data$copied_input_blocks <- as.character(data$copied_input_blocks)

data_filtered = subset(data, type != 'exit_reason')

data_filtered <- ddply(data_filtered, .(layer, tracing_enabled, copied_input_blocks),
                       transform,
                       total_events = sum(freq)
)

data_filtered <- unique(data_filtered[c("layer", "tracing_enabled", "copied_input_blocks", "total_events")])

data_filtered <- ddply(data_filtered, .(layer, copied_input_blocks),
                       transform,
                       tracing_events = abs(sum(total_events)-2*total_events)
)

data_filtered <- unique(data_filtered[c("layer", "copied_input_blocks", "tracing_events")])

data_filtered$event_type <- 'Exits'
# layer,copied_input_blocks,event_type,tracing_events
data_collected_events <- read.table("./io-overhead/data/guest-collected-events.csv", header=T, sep=",")

data_filtered <- merge(x = data_filtered, y = data_collected_events, 
                       by = c("layer","copied_input_blocks","event_type", "tracing_events"), all = TRUE)


data_filtered$copied_input_blocks <- paste(data_filtered$copied_input_blocks,'blocks')

data_filtered$event_type <- as.character(data_filtered$event_type)

data_filtered <- ddply(data_filtered, .(layer, copied_input_blocks),
                       transform,
                       total = sum(tracing_events),
                       max = max(tracing_events)
)
data_filtered$label <- ''
for(i in 1:nrow(data_filtered)) {
  row <- data_filtered[i,]
  if(row$event_type == "Collected"){
    data_filtered[i,]$label = paste(round((row$tracing_events/row$total)*100,1),'%')
  }
}
plot <- ggplot(data_filtered, aes(x=reorder(layer, tracing_events), y = tracing_events)) +
  geom_bar(aes(fill=event_type), position="dodge",stat="identity") +
  scale_y_continuous(breaks = seq(0, max(data_filtered$tracing_events), 10000)) +
  facet_wrap(~copied_input_blocks) +
  # coord_flip() +
  # geom_label_repel(aes(y=tracing_events, label=paste(tracing_events,event_type)),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  geom_text(aes(y=max, label=label ), colour='black', size = 3.4,
            position=position_dodge(width=0.9), vjust=-1) +
  
  # scale_fill_manual(values = colors) +
  labs(x ="Virtualization Layers", y ="Additional exits when enabling tracing", fill="Events types") +
  scale_fill_manual(values = colors) +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    # legend.title=element_blank(),
    axis.text.x = element_text(angle = 40, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)