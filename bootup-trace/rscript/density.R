#!/usr/bin/env Rscript
library(ggplot2)
data=read.table("./bootup-trace/rscript/overhead_kernel_user_space_functions.csv", header=T, sep=',')

data <- subset(data, overhead >= 0 & overhead < 100)
# 
pl<-ggplot(data, aes(x = reorder(function_name, overhead, FUN=median),  function_name, y = overhead )) +
  geom_boxplot(outlier.colour = "red", outlier.size=1) +
  # coord_flip() +
  labs(title = "Function Graph Overhead (Sorted by median)") +
  xlab("Function call") +
  ylab("Overhead %") +
  theme_bw() +
  theme_bw(base_size = 5) +
  theme(legend.position = "top") +
  theme(axis.text.x = element_text(angle = 90, 
                                   hjust = 1, 
                                   vjust = 0))
  # theme(axis.ticks = element_line(size = 1))
plot(pl)