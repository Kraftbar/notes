#!/bin/bash
rm plot.dat
writedata() {
    for i in {1..5}; do
        ping -4 www.google.com | stdbuf -oL sed -n  's/.*time=\([[:digit:]]*\).*/\1/p' >> plot.dat
        sleep 1
        echo "done"
    done
}
 
writedata &
sleep 1

# fix this line with a new one
gnuplot -e " set yrange [0:80];  plot '<(cat plot.dat | tail -7)' using 1 with lines; while (1) { pause 1; replot; };"
