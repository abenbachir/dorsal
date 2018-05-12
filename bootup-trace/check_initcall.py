import os
from os import path
import csv

available_ftrace_fuctions = dict()


with open('logs/available_filter_functions.txt') as f:
    names = f.readlines()
    for name in names:
        available_ftrace_fuctions[name.strip('\n')] = 0



tracable_initcalls = []
with open('logs/initcalls.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        initcall = row['initcall']
        if initcall in available_ftrace_fuctions:
            tracable_initcalls.append(initcall)


print('tracable initcalls=%s', (len(tracable_initcalls)))
print(tracable_initcalls)