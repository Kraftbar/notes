#!/bin/bash

declare -a facilities
facilities_index=0

while read line; do
facility="${line#* nybo-Latitude-7480 }"
facility="${facility%% *}"

  if [[ ! " ${facilities[@]} " =~ " ${facility} " ]]; then
    facilities[facilities_index]=$facility
    facilities_index=$((facilities_index + 1))
  fi
done < /var/log/syslog


