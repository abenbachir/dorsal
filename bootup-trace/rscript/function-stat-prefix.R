#!/usr/bin/env Rscript
library(ggplot2)
library(plyr)
library(scales)
library(ggrepel)
library(stringi)
# function_name,exit_time,duration,depth,process
data_freq <- read.table("./bootup-trace/rscript/bootup-func-frequencies.csv", header=T, sep=",")

data_stat <- ddply(data_freq, "function_name", 
              transform,
              prefix    = paste(unlist(strsplit(as.character(function_name),"[_]"))[1], '_', sep='')
)
data_stat <- count(data_stat, c("prefix"))
data_stat$percentage <- round((data_stat$freq/sum(data_stat$freq)) * 100, 2)
data_stat = subset(data_stat, percentage >= 0.2 )
# colors <- c("#0f2054", "#5f2054", "#ff0d54", "#ff8d54")
colors <- c('18.06 %'="#1f2054", '26.57 %'="#3f2054", '21.56 %'="#9f2d54", '14.65 %'="#6f2d54", '14.65 %'="#1f2054",'1.47 %'= "#ff0d54")


plot <- ggplot(data_stat, aes(reorder(prefix, -percentage))) +
  geom_bar(aes(weight = percentage),  width= 0.7, colour="transparent", fill = '#3f2054') +
  # coord_flip() +
  geom_text(aes(y=percentage, label=paste(percentage,'%') ), color="#3f2054",  fontface = "bold",
            size = 3.5, position=position_dodge(width=0.9), vjust=-1) +
  # scale_fill_manual(values = colors) +
  labs(x ="Function prefix", y ="%") +
  theme_light() +
  theme(
    # legend.position = c(0.94,0.91),
    legend.title=element_blank(),
    # axis.text.x = element_blank(),
    # axis.text.x = element_text(angle = 50, hjust = 1, vjust=1, size = 10),
    axis.text.y = element_text(margin = margin(t=2,b=1))
  )
plot(plot)