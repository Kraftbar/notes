# OpenWrt — SSH + LuCI reachable on WAN
Notes from 2026-09-19. The "WAN" in my setup is a private 192.168.1.0/24 segment behind the
ISP router, so this is LAN-to-LAN exposure, not internet. Re-check that before reusing any of it
(`tracepath -n 1.1.1.1` from behind the box — if hop 2 is public, stop).

## 0. First: LAN and WAN must be different subnets
Mine were both 192.168.1.0/24. Symptom: rules show live in `nft`, ARP for the WAN IP resolves,
but nothing ever completes a handshake — even an explicit Allow-Ping stays silent. Replies to
inbound WAN packets pick the first matching route (br-lan) and leave out the LAN port. This also
silently killed every existing port forward.
```sh
ip route                        # two "192.168.1.0/24 dev ..." lines = broken
uci show network.lan.ipaddr
```
Fix = renumber the LAN. One commit + reboot, never a live `network reload` — you're sitting on the
branch you're cutting. Anything hardcoding the old range (port-forward `dest_ip`) moves in the
same commit.
```sh
cp /etc/config/network  /etc/config/network.bak.$(date +%s)
cp /etc/config/firewall /etc/config/firewall.bak.$(date +%s)
uci set network.lan.ipaddr='192.168.2.1'
uci show firewall | grep dest_ip            # repoint each of these:
uci set firewall.@redirect[0].dest_ip='192.168.2.109'
uci commit network; uci commit firewall
reboot                                       # clients re-DHCP on the new range
```

## 1. SSH on WAN
```sh
uci batch <<'EOT'
add firewall rule
set firewall.@rule[-1].name=Allow-SSH-WAN
set firewall.@rule[-1].src=wan
set firewall.@rule[-1].proto=tcp
set firewall.@rule[-1].dest_port=22
set firewall.@rule[-1].target=ACCEPT
commit firewall
EOT
/etc/init.d/firewall reload
nft list chain inet fw4 input_wan | grep 'dport 22'
```

## 2. LuCI on WAN — on 8443, not 443
80/443 from WAN were already DNAT'd to a LAN host (`uci show firewall | grep redirect`).
Prerouting DNAT runs *before* the input chain, so an input rule for 443 would never match.
```sh
uci add_list uhttpd.main.listen_https='0.0.0.0:8443'
uci commit uhttpd
/etc/init.d/uhttpd restart
uci batch <<'EOT'
add firewall rule
set firewall.@rule[-1].name=Allow-LuCI-WAN
set firewall.@rule[-1].src=wan
set firewall.@rule[-1].proto=tcp
set firewall.@rule[-1].dest_port=8443
set firewall.@rule[-1].target=ACCEPT
commit firewall
EOT
/etc/init.d/firewall reload
```

## 3. Lock it down: key-only SSH
Order matters — prove the key works *before* disabling passwords, or you're locked out.
```sh
# from the desktop
ssh-copy-id root@<router>
# ...or on a box with an empty root password, append it by hand:
# ssh root@<router> "mkdir -p /etc/dropbear; echo '$(cat ~/.ssh/id_ed25519.pub)' >> /etc/dropbear/authorized_keys; chmod 600 /etc/dropbear/authorized_keys"
ssh -o ControlPath=none -o PreferredAuthentications=publickey root@<router> echo OK   # must print OK

# on the router
uci set dropbear.@dropbear[0].PasswordAuth='off'
uci set dropbear.@dropbear[0].RootPasswordAuth='off'
uci commit dropbear; /etc/init.d/dropbear restart

# from the desktop — must say "Permission denied (publickey)"
ssh -o ControlPath=none -o PubkeyAuthentication=no root@<router> true
```
Stock OpenWrt ships an **empty** root password. Dropbear then accepts `none` auth, so a
`BatchMode=yes` login "just works" — that is *not* key auth, don't mistake it for it.
LuCI checks `/etc/shadow` on its own, so key-only dropbear does **not** stop a blank LuCI login.
Set a real password as well:
```sh
passwd          # from a real terminal, so it never lands in a transcript
```

## Gotchas
- **Never paste a long one-liner of `uci set`s.** A terminal wrap split one mid-command:
  `dest_port` got lost, `proto=tcp` + `target=ACCEPT` survived and committed = every TCP port
  open to WAN. Use `uci batch <<'EOT'` (newlines are data there) with `target` on the last line,
  or `ssh host 'sh -s' < file.sh` with `set -e`. The heredoc terminator must sit at column 0 —
  an indented `  EOT` never terminates and the rest of the paste is fed to uci.
- **`ControlMaster` lies to auth tests.** `~/.ssh/config` multiplexes connections; a second `ssh`
  reuses the already-authenticated channel and skips auth entirely, so `-o PubkeyAuthentication=no`
  "succeeds". Always add `-o ControlPath=none` when testing what a server actually accepts.
- **Verify from a host on the WAN segment.** From the LAN you can't reach the WAN IP (other L2),
  and hairpin through the router usually fails too. The honest proof is the rule counter going
  non-zero: `nft list chain inet fw4 input_wan`.
- **Rollback:** `uci delete firewall.@rule[N]; uci commit firewall; /etc/init.d/firewall reload`,
  or restore from `/etc/config/*.bak.*`.
