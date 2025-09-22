#!/bin/sh


find . -iname "statusfile" -type f -print0 | xargs -0 -I {} sh -c 'echo ">>> {}"; cat "{}"'
