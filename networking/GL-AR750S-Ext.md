# GL-AR750S-Ext  
Just some notes on how I configure GL-AR750S-Ext after an reset 
```sh
# Put the pw before running /pasting 
rm $home/.ssh/known_hosts  
ssh root@192.168.1.1
pw='WRITE PASSWORD HERE'
echo -e "$pw\n$pw" | passwd 
uci set wireless.default_radio0.ssid='Un birra mas por favor'
uci set wireless.default_radio0.encryption='sae-mixed'
uci set wireless.default_radio0.key="$pw"
#uci set wireless.default_radio0.disabled=0
uci set wireless.default_radio1.ssid='Un birra mas por favor'
uci set wireless.default_radio1.encryption='sae-mixed'
uci set wireless.default_radio1.key="$pw"
#uci set wireless.default_radio1.disabled=0
uci del wireless.radio0.disabled &> /dev/null
uci del wireless.radio1.disabled &> /dev/null
uci commit wireless
wifi
```



## WAN access (2026-09-19) — SSH + admin panel, key-only
Same idea as `OpenWrt-WAN-access.md`, but GL firmware 4.x serves the panel with **nginx**, not
uhttpd, so the listener lives in a config file rather than uci.
```sh
# firewall: ssh + panel on 8443. 80/443 from WAN are DNAT'd to a LAN host
# (uci show firewall | grep redirect), so 443 can't serve the panel.
uci batch <<'EOT'
add firewall rule
set firewall.@rule[-1].name=Allow-SSH-WAN
set firewall.@rule[-1].src=wan
set firewall.@rule[-1].proto=tcp
set firewall.@rule[-1].dest_port=22
set firewall.@rule[-1].target=ACCEPT
add firewall rule
set firewall.@rule[-1].name=Allow-GLGUI-WAN
set firewall.@rule[-1].src=wan
set firewall.@rule[-1].proto=tcp
set firewall.@rule[-1].dest_port=8443
set firewall.@rule[-1].target=ACCEPT
commit firewall
EOT
/etc/init.d/firewall reload

# nginx: extra https listener. `reload` does NOT bind a new port — it must be `restart`.
cp /etc/nginx/conf.d/gl.conf /etc/nginx/conf.d/gl.conf.bak.$(date +%s)
sed -i '/listen \[::\]:443 ssl;/a\    listen 8443 ssl;' /etc/nginx/conf.d/gl.conf
nginx -t && /etc/init.d/nginx restart
netstat -ltn | grep 8443

# key-only ssh. Prove the key first from the desktop:
#   ssh -o ControlPath=none -o PreferredAuthentications=publickey root@<gl> echo OK
uci set dropbear.@dropbear[0].PasswordAuth='off'
uci set dropbear.@dropbear[0].RootPasswordAuth='off'
uci commit dropbear; /etc/init.d/dropbear restart
```
Notes:
- wan zone input is `DROP` and there is no Allow-Ping, so it won't answer ping from WAN. That's
  by design, not a fault — TCP on 22/8443 still works.
- Nothing in `/etc/init.d/gl*` owns `/etc/config/firewall`; uci rules persist across reloads.
  GL's own "Open Ports on Router" panel writes the same file. Firmware upgrades may still reset it.
- It's a travel router: these rules follow the device to whatever network the WAN is plugged
  into next. Re-check `tracepath` before trusting "the WAN is private".
