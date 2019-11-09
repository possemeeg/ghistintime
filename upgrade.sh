#!/bin/bash

# $1 old-script
# $2 new-script
# $3 old-db
# $4 new-db
#


IFS=$'\n';
for f in $(python3.7 $1 --database $3 get -1 '{c}')
do 
    python3.7 $2 --database $4 put "$f"
done
