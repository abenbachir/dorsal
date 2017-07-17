#!/usr/bin/env Rscript
library(ggplot2)
library(ggrepel)
library(plyr)
# write.csv(data1, file="./hypercall/data/hypercall-host-disabled.csv", row.names = FALSE)
bootup_time_baseline = 868.520 #ms
bootup_time = 2608.425825 # ms
bootup_overhead <- (1 - (bootup_time_baseline/bootup_time))*100

data <- read.table("./bootup-trace/rscript/nested-layer-overhead.csv", header=T, sep=",")

data <- ddply(data, .(nested_level,boot_level),
              transform,
              t_median = median(time),
              t_mean = mean(time)
)
unique_data <- unique(data[c("nested_level", "boot_level", "t_median", "t_mean")])
# unique_data$overhead <- round(100*(1 - bootup_time_baseline/unique_data$median))

p <- ggplot(unique_data, aes(x=reorder(boot_level, -t_median), y=t_median)) +
  # coord_flip() +
  facet_wrap(~boot_level, scale="free") +
  geom_bar(aes(fill=nested_level),position="dodge",stat="identity") +
  # geom_text(aes(label=paste('overhead','%') ), colour='white',  fontface = "bold",
  #           # label.padding = unit(0.5, "lines"),
  #           # label.r = unit(0.7, "lines"),
  #           # label.size = 0,
  #           size = 5,
  #           position=position_dodge(width=0.9), hjust=2) +
  # coord_flip() +
  # scale_fill_manual(values = colors) +
  # geom_hline(yintercept = c(baseline), linetype="dotted") +
  labs(x ="", y ="Nanoseconds", fill = "Traced events") +

  theme_light() +
  theme(
    # legend.position="none",
    axis.text.y = element_text(size=12),
    # axis.text.x = element_text(size=14),
    axis.text.x = element_text(angle = 40, hjust = 1, vjust=1, size = 10)
  )

plot(p)