#!/bin/bash -x

## como hacer el setup de dropbox???


# read the ss.dropbox.key
line=$(head -n 1 ss.dropbox.key)
# parse user and password
IFS=':' read -r -a array <<< "$line"

user=${array[0]}
pass=${array[1]}

python linker.py -u $user -p $pass