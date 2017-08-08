#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)

# layer,tracing_enabled,type,freq,event
data_10 <- read.table("./io-overhead/data/io-exits-10.csv", header=T, sep=",")
data_100 <- read.table("./io-overhead/data/io-exits-100.csv", header=T, sep=",")
data_1000 <- read.table("./io-overhead/data/io-exits-1000.csv", header=T, sep=",")

data_10$copied_input_blocks <- 10
data_100$copied_input_blocks <- 100
data_1000$copied_input_blocks <- 1000

data <- rbind(data_10, data_100, data_1000)

data$tracing_enabled <- as.character(data$tracing_enabled)

data_filtered = subset(data, type != 'exit_reason')

data_filtered <- ddply(data_filtered, .(layer, tracing_enabled, copied_input_blocks),
              transform,
              total_events = sum(freq)
)

data_filtered <- unique(data_filtered[c("layer", "tracing_enabled", "copied_input_blocks", "total_events")])

data_filtered <- ddply(data_filtered, .(layer, copied_input_blocks),
                       transform,
                       diff_events = abs(sum(total_events)-2*total_events)
)

  
plot <- ggplot(data_filtered, aes(x=reorder(layer, total_events), y = total_events)) +
  geom_bar(aes(fill=tracing_enabled), position="dodge",stat="identity") +
  facet_wrap(~copied_input_blocks, scale="free") +
  # coord_flip() +
  # geom_label_repel(aes(y=freq, label=paste(data_freq$percentage, "%")),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  geom_text(aes(y=total_events, label=paste(diff_events,'events') ), colour='black', size = 3.4,
            position=position_dodge(width=0.9), vjust=-1) +
  # scale_fill_manual(values = colors) +
  labs(x ="Exit events", y ="Frequency") +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    legend.title=element_blank(),
    axis.text.x = element_text(angle = 40, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)