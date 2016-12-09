#!/usr/bin/python3

import sys
import json
import os
import getopt
import sys
import babeltrace.reader
from symbols import Symbols

content = json.load(open("./traces/overhead_traces.json", "r"))
functions = content["func_overheads"]
with open("./rscript/overhead_functions.csv", "w") as f:
    f.write("function_name,overhead\n")
    for function_name, overheads in functions.items():
        for overhead in overheads:
            f.write('"{}",{}\n'.format(function_name,overhead))
# print(content)




