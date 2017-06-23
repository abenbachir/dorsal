#!/usr/bin/env Rscript
library(ggplot2)
library(plyr)
library(scales)
library(ggrepel)
library(stringi)
# function_name,exit_time,duration,depth,process

filters <- c('note_page',
            'kmem_cache_alloc','kmem_cache_free',
            '__slab_free',
            'acpi_*',
            '_raw_spin_*',
            'mutex_*',
            '_cond_resched','console_conditional_schedule','console_trylock','console_unlock'
          )
data <- read.table("./bootup-trace/bootup-functions.csv", header=T, sep=",")


grep(glob2rx("acpi_*"), data, value = TRUE)


acpi <- subset(data,  grepl(glob2rx("acpi_*") , function_name) )