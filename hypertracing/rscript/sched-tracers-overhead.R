#!/usr/bin/env Rscript
# install.packages("reshape2")
library(ggplot2)
library(ggrepel)
library(plyr)
library(reshape2)
source("./hypertracing/rscript/global.R")
# layer,tracer,workload,configuration,time,event,freq,total_event_cost,cost_per_event
data <- read.table("./hypertracing/data/sched-tracers-overhead.csv", header=T, sep=",")

data = subset(data, event != 'HLT')
# data = subset(data, configuration == 'getcpu_0_2500')
data = subset(data, layer == 'L1')
data_filtered <- ddply(data, .(layer, tracer, workload, configuration, event),
                       transform,
                       total_event_cost_avg = mean(total_event_cost)
)
data_filtered <- ddply(data_filtered, .(layer, tracer, workload, configuration),
                       transform,
                       time_avg = median(time)/10**3
)
data_filtered <- unique(data_filtered[c("layer", "tracer", "workload", "configuration", "time_avg", 
                                        "event", "total_event_cost_avg")])

# print(data_filtered)
data_filtered <- ddply(data_filtered, .(layer, tracer, workload, configuration),
                       transform,
                       total_exits_cost = sum(total_event_cost_avg)/10**3,
                       time_std = sd(time_avg)/10**3
)

data_filtered <- unique(data_filtered[c("layer", "tracer", "workload", "configuration", "time_avg", 
                                        "time_std", "total_exits_cost")])



data_filtered <- ddply(data_filtered, .(layer, workload, configuration),
                       transform,
                       baseline = min(time_avg) 
)

# baseline = data_filtered$time_avg[data_filtered$tracer == 'None']

# compute total overhead
data_filtered$overhead <- paste(round((1 - data_filtered$baseline/data_filtered$time_avg)*100,2),'%', sep='')

# data_filtered$overhead <- paste(data_filtered$overhead,'\nx',round((data_filtered$time_avg/data_filtered$baseline),2),sep ='')

# compute exit overhead
data_filtered$exit_overhead <- paste(round((1 - data_filtered$workload_time/data_filtered$time_avg)*100,2),'%')
data_filtered$workload_time <- data_filtered$time_avg - data_filtered$total_exits_cost

data_filtered <- melt(data_filtered, id.vars=c("layer", "tracer", "workload", "configuration", "baseline",
                                               "overhead", "time_std", "exit_overhead","time_avg"))

plot <- ggplot(data_filtered, aes(x=reorder(tracer, time_avg), y = value)) +
  geom_bar(aes(), position="dodge",stat="identity") +
  scale_y_continuous(breaks = seq(0, max(data_filtered$time_avg), 500)) +
  # facet_wrap(layer~configuration, ncol=2) +
  # coord_flip() +
  # geom_label_repel(aes(y=tracing_events, label=paste(tracing_events,event_type)),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  geom_text(aes(y=time_avg, label=overhead ), colour='black', size = 3.4,
            position=position_dodge(width=0.9), vjust=-1) +
  # 
  # scale_fill_manual(values = colors) +
  labs(title = "Micro-Benchmarks Tracing sched_switch [about 6000 events]",x ="Tracers", y ="Workload and Exits Cost (us)", fill="Cost of") +
  # scale_fill_manual(values = colors) +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    # legend.title=element_blank(),
    axis.text.x = element_text(angle = 20, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)