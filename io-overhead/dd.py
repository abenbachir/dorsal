import os
import os.path
import sys
import time
import re
import subprocess
import socket
"""
    I/O: Measuring Write Performance
"""

if __name__ == "__main__":
    argv = sys.argv[1:]
    tracing_enabled = 0
    iterations = 1
    hostname = socket.gethostname()
  
    cmd1 = "dd if=/dev/zero of=/tmp/test bs=1K count=500 conv=fdatasync"
    cmd2 = "dd if=/dev/zero of=/tmp/test bs=1K count=500 oflag=sync iflag=sync"
    
    cmd = cmd1
    try:
        if len(argv) >= 1:
            iterations = int(argv[0])
        if len(argv) >= 2:
            tracing_enabled = argv[1]

    except Exception as ex:
        print(ex)

    benchmarkDir = "./"
    if not os.path.exists(benchmarkDir):
        os.makedirs(benchmarkDir)

    filename = benchmarkDir+"/"+hostname+"-dd.csv"
    exits = os.path.exists(filename)
    f = open(benchmarkDir+"/"+hostname+"-dd.csv", 'a')
    if not exits:
        f.write("hostname,time,speed,size,tracing_enabled\n")

    for iteration in xrange(iterations):
        lines = subprocess.Popen(cmd.split(' '),
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT).stdout.readlines()
        # 1048576 bytes (1.0 MB, 1.0 MiB) copied, 0.00603379 s, 174 MB/s
        values = filter(None, re.split(',|\(|\)', lines[2].strip('\n')))
        measured_time = values[4].strip(' ').split(' ')[0]
        size = values[0].strip(' ').split(' ')[0]
        speed = values[5].strip(' ').split(' ')[0]
        f.write("%s,%s,%s,%s,%s\n" % (hostname,measured_time ,speed, size, tracing_enabled))
        # time.sleep(1)

    f.close()
