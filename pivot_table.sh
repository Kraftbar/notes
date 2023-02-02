#!/bin/sh

# Create an associative array to store the count of each facility
declare -A facility_count

# Create an array to store all facilities
declare -a facilities

# Read the syslog file
while read line; do
  # Extract the time and facility from each line
  time=$(echo $line | awk '{print $2}')
  facility=$(echo $line | awk -F "[][]" '{print $2}' | awk -F ":" '{print $1}')

  # Add the facility to the array of facilities if it doesn't already exist
  if ! [[ " ${facilities[@]} " =~ " ${facility} " ]]; then
    facilities+=($facility)
  fi

  # Increase the count of the facility in the associative array
  if [ "${facility_count[$time,$facility]+_}" ]; then
    facility_count[$time,$facility]=$((${facility_count[$time,$facility]} + 1))
  else
    facility_count[$time,$facility]=1
  fi
done < /var/log/syslog

# Print the header
echo "time,"$(echo "${facilities[@]}" | tr " " ",")

# Sort the associative array by time
sorted_times=$(echo "${!facility_count[@]}" | tr " " "\n" | awk -F "," '{print $1}' | sort | uniq)

# Iterate over the sorted times
for time in $sorted_times; do
  # Create a string to store the count of each facility for the current time
  count_string=""

  # Count the number of occurrences of each facility for the current time
  for facility in "${facilities[@]}"; do
    if [ "${facility_count[$time,$facility]+_}" ]; then
      count_string="$count_string,${facility_count[$time,$facility]}"
    else
      count_string="$count_string,0"
    fi
  done

  # Print the time and count string
  echo "$time$count_string"
done
