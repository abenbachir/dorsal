#!/usr/bin/env bash

linuxsource="linux"
linuxtarget="linux"
target="host"

scp $target:~/$linuxtarget/kernel/trace/trace_hypergraph.c ~/$linuxsource/kernel/trace/
scp $target:~/$linuxtarget/kernel/trace/trace_hyperlevel.c ~/$linuxsource/kernel/trace/

scp $target:~/$linuxtarget/kernel/trace/Makefile ~/$linuxsource/kernel/trace/
scp $target:~/$linuxtarget/kernel/trace/trace.c ~/$linuxsource/kernel/trace/
scp $target:~/$linuxtarget/kernel/trace/trace.h ~/$linuxsource/kernel/trace/

scp $target:~/$linuxtarget/init/main.c ~/$linuxsource/init/
scp $target:~/$linuxtarget/init/Makefile $linuxsource/init/

cd $linuxsource
make -j$(nproc) && sudo make modules_install && sudo make install;
cd ..