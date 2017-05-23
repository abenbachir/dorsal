#!/usr/bin/env Rscript
library(ggplot2)
library(stringi)

# data_functions <- read.table("/home/abder/functions.csv", header=T, sep=",")

themes = theme_bw() +
  theme(
    plot.title =  element_text(family="Helvetica", margin = margin(b=15), size=12),
    legend.position = "none",
    axis.text.x = element_text(margin = margin(t=2,b=15), size = 10)
  )

data_test = subset(data, function_name == 'mutex_lock' | function_name == 'mutex_unlock')
p <- ggplot(data_test, aes(duration, colour=as.character(function_name))) +
  facet_wrap( ~ function_name, scale= "free") +
  geom_density() +
  # labs(title = 'Multimodal Distribution') +
  xlab("") +
  ylab("Density") +
  xlim(0, 2000)+
  themes


# pdf(file="./plots/all_functions_distribution.pdf", width=50, height=50)
plot(p)
# dev.off()