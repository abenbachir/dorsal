#!/bin/bash

# inspired from http://cgit.openembedded.org/cgit.cgi/openembedded/tree/contrib/patchwork/pw-am.sh
# This script will fetch an 'mbox' patch from patchwork and git am it
# usage: pw-am.sh <number>
# example: 'pw-am.sh 221' will get the patch from http://patchwork.ozlabs.org/patch/221/

if [ "$1" == "" ]; then
	echo "missing patch id, use the script as: example 'pw-am.sh 221' "
	exit 1
fi

for patchnumber in $1;
do
	wget -nv http://patchwork.ozlabs.org/patch/$patchnumber/mbox/ -O pw-am-$patchnumber.patch
	git am -s pw-am-$patchnumber.patch
	rm pw-am-$patchnumber.patch
done

