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
            '*console*'
          )
data <- read.table("./bootup-trace/rscript/bootup-func-frequencies.csv", header=T, sep=",")

total <- sum(data$freq)

acpi <- subset(data,  grepl(glob2rx("*acpi*") , function_name) )

slab <- subset(data,  grepl(glob2rx("*slab*") , function_name) )

raw_spin <- subset(data,  grepl(glob2rx("_raw_spin*") , function_name) )

console <- subset(data,  grepl(glob2rx("*console*") , function_name) )

kmem_cache <- subset(data,  grepl(glob2rx("*kmem_cache*") , function_name) )

reste <- subset(data, grepl(paste(filters, collapse = '|'), function_name, invert=TRUE))