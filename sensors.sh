upower -i $(upower -e | grep 'BAT') | grep --color=never -E percentage | awk '{print $2}'
echo "Wi-Fi Signal Strength: $(iwconfig 2>&1 | awk -F '[ =]+' '/Quality/ {print $4}')"
iwconfig 2>&1 | grep "Bit Rate"  |  awk '{print $1 " " $2 " " $3}'
ip addr | awk ' /(inet)(.*)brd/ {print $2 }'
iwlist scan 2>&1 | grep -A22 -B5 -i "por "

iw dev wlp2s0 info | awk '/width/ {print "Width " $6 "MHz"}'
iw dev wlp2s0 info | awk '/channel/ {print "Channel " $2}'
iw dev wlp2s0 info | awk '/channel/ {print "Center " $3 }' | sed 's/(//'
iw dev wlp2s0 info | awk '/channel/ {print "Center " $9 }' 
