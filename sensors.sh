upower -i $(upower -e | grep 'BAT') | grep --color=never -E percentage | awk '{print $2}'
echo "Wi-Fi Signal Strength: $(iwconfig 2>&1 | awk -F '[ =]+' '/Quality/ {print $4}')"
iwconfig 2>&1 | grep "Bit Rate"  |  awk '{print $1 " " $2 " " $3}'
ip addr | awk ' /(inet)(.*)brd/ {print $2 }'
iwlist scan 2>&1 | grep -A22 -B5 -i "por "
