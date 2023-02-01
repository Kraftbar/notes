#!/bin/bash

if [ -p /dev/stdin ]; then
  # input is from a pipe
  read -r args
else
  # input is from arguments
  args="$@"
fi

# process the arguments
i=1
while [ "$args" ]; do
  eval "arg$i=\${args%% *}"
  if [ "$args" = "${args#* }" ]; then
    args=""
  else
    args="${args#* }"
  fi
  i=$((i+1))
done

# output the arguments
for ((j=1; j<i; j++)); do
  echo "arg$j: $(eval "echo \$arg$j")"
done
