#!/usr/bin/env Rscript
library(ggplot2)
library(plyr)
library(scales)
library(ggrepel)
library(stringi)
# function_name,exit_time,duration,depth,process

filters <- c('note_page',
            '*kmem_cache*',
            '*slab*',
            '*acpi*',
            '_raw_spin_*',
            '*mutex*',
            '_cond_resched',
            '*console*',
            '*fb*'
          )
data <- read.table("./bootup-trace/rscript/bootup-func-frequencies.csv", header=T, sep=",")

total <- sum(data$freq)

reste <- subset(data, !grepl(paste(filters, collapse = '|'), function_name))

data_stat = data.frame(filter = 'reste', 
                       total_func = length(reste$function_name), 
                       total_freq = sum(reste$freq), 
                       percentage = round(100 * (sum(reste$freq)/total), 2))

for (filter in filters) 
{
  result = subset(data,  grepl(glob2rx(filter) , function_name))
  new_row = data.frame(filter = filter, 
                       total_func = length(result$function_name), 
                       total_freq = sum(result$freq), 
                       percentage = round(100 * (sum(result$freq)/total), 2))

  data_stat <- rbind(data_stat, new_row)
}
colors <- c("#6f2d54", "#1f2054", "#ff0d54", "#1f2054", "#3f2054", "#9f2d54", "#6f2d54", "#1f2054", "#ff0d54")
data_stat <- subset(data_stat, filter != 'reste')

plot <- ggplot(data_stat, aes(reorder(filter, -total_freq))) +
  geom_bar(aes(weight = total_freq),  width= 0.7, colour="white") +
  coord_flip() +
  # geom_label_repel(aes(y=freq, label=paste(data_freq$percentage, "%")),
  #                  size = 3, segment.size = 0.3, colour="black", fill="white",
  #                  min.segment.length = unit(0, "lines"), nudge_x = 0
  # ) +
  geom_text(aes(y=total_freq, label=paste(percentage,'%') ), colour='black', size = 3.4,
            position=position_dodge(width=0.9), hjust=-0.1) +
  # scale_fill_manual(values = colors) +
  labs(x ="Filters", y ="Frequency") +
  theme_light() +
  theme(
    legend.position = c(0.94,0.91),
    legend.title=element_blank(),
    # axis.text.x = element_blank(),
    # axis.text.x = element_text(angle = 20, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)


