#!/usr/bin/env Rscript
# install.packages("reshape2")
library(ggplot2)
library(ggrepel)
library(plyr)
library(reshape2)
library(stringi)
# bleu ciel -> #3faff4
# deeppink
# lightseagreen
# deepskyblue4
# dodgerblue4
# #5f1f84
# #cf1f54 => hypercall
# #ffd204 => yellow
# #3faf1f
colors <- c("Baseline" = "gray10", "Guest Tracing" = "#6f2054", "Write to disk"="dodgerblue2",
            "Host Tracing" = "#2f1f54", "Hypercall" = "#cf1f54", 
            "Syscall Probe"="darkorange2", "Time+Compression"="yellow2", "Nested Cost"="#3faf1f")

# layer,tracer,workload,configuration,time,event,freq,total_event_cost,cost_per_event
data <- read.table("./hypertracing/data/syscall-nutshell-overhead-10e.csv", header=T, sep=",")
data$can_show_overhead <- FALSE
data$can_show_overhead[data$component == "Guest Tracing" | data$component == "Hypercall"] <- TRUE

# data = subset(data, layer == 'L1')
# data = subset(data, tracer != 'Strace')
# data = subset(data, !startsWith(as.character(tracer), 'Hypertracing +') )

data = subset(data, component != 'Baseline')
data <- ddply(data, .(layer, tracer, workload, configuration),
                       transform,
                       total_time = round(sum(time),1)
)

# data <- ddply(data[data$can_show_overhead == "True"], .(layer, tracer, workload, configuration),
#               transform,
#               overhead = round(1 - (baseline/total_time),1)
# )

# data$overhead[data$can_show_overhead == "True"] <- paste(round((1 - data_filtered$baseline/data_filtered$time_avg)*100,1),'%', sep='')
# 
# data$overhead <- paste(data_filtered$overhead,'\nx',round((data_filtered$time_avg/data_filtered$baseline),1),sep ='')

data$overhead <- ''
for(i in 1:nrow(data)) {
  row <- data[i,]
  if(row$can_show_overhead)
  {
    overhead = round((1-(row$baseline/row$total_time))*100,1)
    multiple = round((row$total_time/row$baseline),1)
    data[i,]$overhead <- paste(row$total_time,'ns', sep=' ')
    # if(overhead > 50){
    #   data[i,]$overhead <- paste('x',multiple, sep='')
    # }else{
    #   data[i,]$overhead <- paste(overhead,'% \nx', multiple, sep='')
    # }
    
    # data[i,]$overhead <- paste(round( (1-(row$baseline/row$total_value))*100  ,1),'%')
  }else{
    # data[i,]$overhead <- ''
  }
}

plot <- ggplot(data, aes(x=reorder(tracer, total_time), y = time)) +
  # geom_bar(aes(fill=component ), position="stack",stat="identity") +
  geom_col(aes(fill=component ), position=position_stack(reverse = TRUE)) +
  # scale_y_continuous(breaks = seq(0, max(data$total_time), 200)) +
  facet_wrap(~layer, ncol=2) +
  # coord_flip() +
  # geom_label_repel(aes(y=tracing_events, label=paste(tracing_events,event_type)),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  geom_text(aes(y=total_time, label=overhead), colour='black', size = 3.4,
            position=position_dodge(width=0.9), vjust=-1) +
  labs(title = "Micro-Benchmarks Tracing getCPU Syscall [5000 events]", x ="Tracers", y ="Latency (ns)", fill="Cost of") +
  scale_fill_manual(values = colors) +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    # legend.title=element_blank(),
    axis.text.x = element_text(angle = 20, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)