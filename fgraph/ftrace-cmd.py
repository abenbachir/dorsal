#!/usr/bin/env python

import argparse
import os
import sh

t = "/sys/kernel/debug/tracing"

def write_to(base, name, data):
    with open(os.path.join(base, name), "w") as f:
        f.write(data)

def enable_ftrace(args):
    write_to(t, "current_tracer", "function_graph")
    write_to(t, "set_graph_function", "vfs_fstat")
    write_to(t, "tracing_on", "1")

def disable_ftrace(args):
    write_to(t, "tracing_on", "0")

def show_trace(args):
    print sh.cat(t+"/trace")

def list_options(args):
    print sh.ls(t)

def status(args):
    current_tracer = sh.cat(t+"/current_tracer").strip()
    is_enabled = sh.cat(t+"/tracing_on").strip() == "1"
    print "current_tracer", ("enabled" if is_enabled else "disabled")

if __name__=="__main__":


    cmds = { "enable": enable_ftrace,
             "disable": disable_ftrace,
             "show": show_trace,
             "list": list_options,
             "status": status
    }

    def not_a_command(args):
        print("unkown command")

    parser = argparse.ArgumentParser()
    parser.add_argument("cmd")
    args = parser.parse_args()
    c = cmds.get(args.cmd, not_a_command)
    c(args)