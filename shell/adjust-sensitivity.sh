nybo@nybo-Latitude-7480:~$ xinput --set-prop "DLL07A0:01 044E:120B" "Device Accel Constant Deceleration" 1.1

nybo@nybo-Latitude-7480:~$ test="$(for i in $(seq 1 20); do xinput list-props $i | awk -v i=$i '{print i, $0}'  2>/dev/null; done)"
