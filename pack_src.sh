#!/bin/bash
filename = $(pwd)/src_mcServerControl.zip
# if [ -f $filename ]; then
#    rm $filename
#    echo "$filename is removed"
# fi
zip -r $filename $(git ls-files)
