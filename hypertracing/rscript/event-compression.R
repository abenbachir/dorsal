#!/usr/bin/env Rscript
# install.packages("reshape2")
library(ggplot2)
library(ggrepel)
library(plyr)
library(reshape2)
library(stringi)
library(scales)
source("./hypertracing/rscript/global.R")
# layer,tracer,compressed_event,workload,configuration,time,event,freq,total_event_cost,cost_per_event
data <- read.table("./hypertracing/data/event-compression.csv", header=T, sep=",")

# data$nb_events <- 
hypercall_arguments = 9
time_delta_per_arg = 2

data_filtered <- ddply(data, .(layer, tracer, compressed_event, workload, configuration),
                       transform,
                       nb_events = as.integer(strsplit(as.character(unique(configuration)),"_")[[1]][3])
)
data_filtered <- ddply(data_filtered, .(layer, tracer, compressed_event, workload, configuration),
                       transform,
                       time_avg = mean(time)/nb_events,
                       time_median = median(time)/nb_events,
                       time_std = sd(time)/nb_events
)

data_filtered <- unique(data_filtered[c("layer", "tracer", "compressed_event", "workload", "configuration", "nb_events","time_avg", "time_median", "time_std")])


data_filtered <- ddply(data_filtered, .(layer, workload, configuration),
                       transform,
                       baseline = min(time_avg)
)

data_filtered$time <- data_filtered$time_avg - data_filtered$baseline

data_filtered$time_diff <- data_filtered$time_avg - data_filtered$baseline
# baseline = data_filtered$time_avg[data_filtered$tracer == 'None']

# compute total overhead
data_filtered$overhead <- round((1 - data_filtered$baseline/data_filtered$time)*100,1)
# data_filtered$overhead <- paste(round((1 - data_filtered$baseline/data_filtered$time)*100,1),'%', sep='')

# data_filtered$overhead <- paste(data_filtered$overhead,'\nx',round((data_filtered$time/data_filtered$baseline),2),sep ='')
data_filtered$overhead <- round((data_filtered$time/data_filtered$baseline),2)

# data_filtered <- melt(data_filtered, id.vars=c("layer", "tracer", "workload", "configuration", "time_avg","time_median",
# "time_std", "baseline", "overhead"))

data_filtered$args_for_time_delta <- (data_filtered$compressed_event-1)/time_delta_per_arg
data_filtered$args_for_time_delta[data_filtered$args_for_time_delta < 0] <- 0
data_filtered$args_for_payload <- hypercall_arguments - data_filtered$args_for_time_delta
data_filtered$args_for_payload[data_filtered$args_for_payload < 0] <- 0
compression <- subset(data_filtered, tracer == "Event Compressing" )
lttng <- subset(data_filtered, tracer == "Lttng" )
ftrace <- subset(data_filtered, tracer == "Ftrace" )
perf <- subset(data_filtered, tracer == "Perf" )

data_filtered = subset(data_filtered, startsWith(as.character(tracer),"Hyper") )
data_filtered = subset(data_filtered, (args_for_payload %% 1) == 0 | compressed_event == 2 | compressed_event == 4)

compression_overhead = compression$time
lttng_overhead = lttng$time_avg - 510
ftrace_overhead = ftrace$time_avg - 510
perf_overhead = perf$time_avg - 510
baseline = compression$baseline

compression_color = "darkorange2"
ftrace_color = "deepskyblue4"
lttng_color = "#6f2054"
perf_color = "deeppink"
plot <- ggplot(data_filtered, aes(compressed_event, time)) +
  scale_x_continuous(breaks = seq(0, max(data_filtered$compressed_event), 1)) +
  scale_y_continuous(breaks = seq(0, max(data_filtered$time), 25)) +
  geom_point(aes(), size=1.5) +  
  # geom_point(aes(), size=data_filtered$args_for_payload*2, shape=1, stroke=1) +
  geom_line() +
  
  geom_hline(yintercept = c(compression_overhead), linetype="dashed", color=compression_color) +
  geom_hline(yintercept = c(lttng_overhead), linetype="dashed", color=lttng_color) +
  geom_hline(yintercept = c(ftrace_overhead), linetype="dashed", color=ftrace_color) +
  geom_hline(yintercept = c(perf_overhead), linetype="dashed", color=perf_color) +
  geom_hline(yintercept = c(0), linetype=0) +
  # geom_vline(xintercept = c(data_filtered$compressed_event), linetype="3313") +
  # geom_segment(aes(x = data_filtered$compressed_event, y = 0, xend = data_filtered$compressed_event, yend = time),
  #              size=0.3, linetype=1, data = data_filtered) +
  

  # geom_point(aes(x=2,y=0.6), colour= muted("red"), shape=1, size=7) +
  # geom_label(aes(x=compressed_event+0.3,y=time+80, label=paste(args_for_payload,"args")),
  #   fill = muted("red"), colour = "white", fontface = "bold", nudge_x = 1, nudge_y=0.3) +
  geom_label_repel(aes(y=time, label=paste(args_for_payload*8,"Bytes\npayload")),
                   size = 3.2, segment.size = 0.5, colour="white", segment.color=muted("red"),  fill = muted("red"),
                   min.segment.length = unit(0, "lines"), nudge_x = 1.5, nudge_y = 20
  ) +
  # geom_text(aes(y=baseline, x = 0, label="Baseline" ), colour='black', size = 3.4,
  #           position=position_dodge(width=0.9), vjust=-0.15) +
  # 
  # annotate("text", x = 1, y = baseline+baseline*0.2, label = "Baseline                     ") +
  annotate("label", x = 19, y = lttng_overhead, label = "      Lttng      ", color="white", fill=lttng_color,
             label.padding = unit(0.45, "lines")) +
  annotate("label", x = 19, y = ftrace_overhead, label = "     Ftrace     ", color="white", fill=ftrace_color,
             label.padding = unit(0.45, "lines")) +
  annotate("label", x = 19, y = perf_overhead, label = "      Perf      ", color="white", fill=perf_color,
           label.padding = unit(0.45, "lines")) +
  annotate("label", x = 19, y = compression_overhead, label = "Compression", color="white", fill=compression_color,  
             label.padding = unit(0.45, "lines")) +
  labs(title = "Offloading Latency of a Hypercall When Enabling Event Compression",x ="Number of compressed events", y ="Latency (ns)", fill="Cost of") +
  # scale_fill_manual(values = colors) +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    # legend.title=element_blank(),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)